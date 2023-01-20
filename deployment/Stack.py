import os
import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_deployment as s3deploy
import aws_cdk.aws_glue_alpha as glue
import aws_cdk.aws_iam as iam
import json

account_id = os.getenv('AWS_ACCOUNT')


class TDGCdkStack(cdk.Stack):

    def __init__(self, scope: cdk.App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        artefact_bucket = s3.Bucket(self, f'tdg-artefacts-{account_id}',
                                    bucket_name=f'tdg-artefacts-{account_id}',
                                    versioned=True
                                    )

        s3deploy.BucketDeployment(self, "DeployTGDLib",
                                  sources=[s3deploy.Source.asset("./Lib")],
                                  destination_bucket=artefact_bucket,
                                  destination_key_prefix="tgd_lib/"
                                  )

        s3deploy.BucketDeployment(self, "DeployGlueJob",
                                  sources=[s3deploy.Source.asset("./Glue")],
                                  destination_bucket=artefact_bucket,
                                  destination_key_prefix="tgd_glue_job/"
                                  )

        iam_role_name = "TDG_Glue_Role"
        tgd_glue_role = iam.Role(self, "TDG_Glue_Role",
                                 assumed_by=iam.ServicePrincipal(
                                     "glue.amazonaws.com")
                                 )
        tgd_glue_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'))
        tgd_glue_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonDynamoDBFullAccess'))

        self.create_managed_policies(f"{iam_role_name}_policy", tgd_glue_role)

        glue.Job(self, "TDGPysparkJOb",
                 executable=glue.JobExecutable.python_etl(
                     glue_version=glue.GlueVersion.V3_0,
                     python_version=glue.PythonVersion.THREE,
                     script=glue.Code.from_bucket(
                         artefact_bucket, "tgd_glue_job/Job/TDGGlueJob.py"),
                     extra_python_files=[
                            glue.Code.from_bucket(artefact_bucket, "tgd_lib/TestDataGeneratorLib.py"), 
                            glue.Code.from_bucket(artefact_bucket, "tgd_lib/TestDataGeneratorTargets.py")
                        ],
                     extra_files=[glue.Code.from_bucket(
                         artefact_bucket, "tgd_glue_job/Config/TDG_configuration_file.yml")],
                 ),
                 job_name="TestDataGeneratorJob",
                 description="Test Data Generator main Glue job",
                 default_arguments={
                     "--config_file_path": f"{artefact_bucket.bucket_name}/tgd_glue_job/Config/TDG_configuration_file.yml"},
                 role=tgd_glue_role
                 )

    def create_managed_policies(self, dir, role, role_name=None) -> iam.Role:
        dir = f"./deployment/iam_policies/{dir}/"
        if os.path.isdir(dir):
            for file in os.listdir(dir):
                with open(dir + file) as json_file:
                    data = json_file.read()
                    data = data.replace("**AWS_ACCOUNT_ID**", account_id)
                    policy_name = file.replace(".json", "")
                    logical_policy_name = policy_name

                    if role_name is not None:
                        logical_policy_name = f"{role_name}-policy"

                    data = json.loads(data)
                    policy = iam.PolicyDocument.from_json(data)
                    policy = iam.ManagedPolicy(self,
                                               policy_name + "pol",
                                               managed_policy_name=logical_policy_name,
                                               document=policy)

            policy.attach_to_role(role)

        return role
