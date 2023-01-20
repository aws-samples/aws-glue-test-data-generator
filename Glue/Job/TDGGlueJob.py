import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.types import StringType
from pyspark.sql.functions import col
import boto3,yaml
from TestDataGeneratorLib import TestDataGeneratorLib
from TestDataGeneratorTarg import TestDataGeneratorTarg

#Initialization
args = getResolvedOptions(sys.argv, ["JOB_NAME","config_file_path"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

### Test Data Generator main  function

def _main_test_data_generator():

    s3_client = boto3.client('s3')
    bucket_name, config_file_key = args['config_file_path'].split('/', 1) 

    response = s3_client.get_object(Bucket=bucket_name, Key=config_file_key)

    config_file = yaml.safe_load(response["Body"])

    number_of_generated_records = config_file['number_of_generated_records']
    tgd = TestDataGeneratorLib(spark,number_of_generated_records)
    tgd_targets = TestDataGeneratorTarg(glueContext)
    generated_df = spark.range(0,number_of_generated_records , 1)
    generated_df = generated_df.withColumn("id",col("id").cast(StringType())) 
    
    #Test Data Generation
    for atribute_config in config_file['attributes_list']:
        fn = getattr(tgd,atribute_config["Generator"])
        generated_df = fn(generated_df,atribute_config["DataDescriptor"] , atribute_config["ColumnName"])
        
    generated_df = generated_df.drop("id")
    
    #Test Output writing 

    for target_config in config_file['target_list']:
        fn = getattr(tgd_targets,target_config["target"])
        fn(generated_df,target_config["attributes"])    
    
    job.commit()
    
_main_test_data_generator()