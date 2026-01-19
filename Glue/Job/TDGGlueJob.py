import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.types import StringType
from pyspark.sql.functions import col
import boto3, yaml, logging
from TestDataGeneratorLib import DataGeneratorLib
from TestDataGeneratorTarg import DataGeneratorTarg

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialization
args = getResolvedOptions(sys.argv, ["JOB_NAME", "config_file_path"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

### Test Data Generator main  function


def _main_test_data_generator():
    """
    This function is the main entry point for the Test Data Generator application. It uses the TestDataGeneratorLib and TestDataGeneratorTarg classes to generate test data and write it to output targets.

    The function expects a YAML configuration file that contains the following parameters:
    - number_of_generated_records: The number of records to generate.
    - attributes_list: A list of attributes to be generated, along with their configuration details.
    - target_list: A list of output targets, along with their configuration details.

    Configuration can be provided in two ways:
    1. As a YAML string via the --config_yaml parameter
    2. As an S3 path via the config_file_path parameter (fallback)

    :return: None
    """

    # Check if config_yaml parameter is provided
    config_yaml_arg = None
    for arg in sys.argv:
        if arg.startswith('--config_yaml'):
            if '=' in arg:
                config_yaml_arg = arg.split('=', 1)[1]
            else:
                # Handle case where value is in next argument
                idx = sys.argv.index(arg)
                if idx + 1 < len(sys.argv):
                    config_yaml_arg = sys.argv[idx + 1]
            break
    
    logger.info(f"Parsed config_yaml_arg: {config_yaml_arg}")
    
    if config_yaml_arg:
        # Use the provided YAML configuration
        config_file = yaml.safe_load(config_yaml_arg)
        logger.info(f"Using provided YAML configuration: {config_yaml_arg}")
    else:
        # Fallback to reading from S3
        s3_client = boto3.client("s3")
        bucket_name, config_file_key = args["config_file_path"].split("/", 1)
        response = s3_client.get_object(Bucket=bucket_name, Key=config_file_key)
        config_yaml_content = response["Body"].read().decode('utf-8')
        config_file = yaml.safe_load(config_yaml_content)
        logger.info(f"Using S3 YAML configuration from {args['config_file_path']}: {config_yaml_content}")

    number_of_generated_records = config_file["number_of_generated_records"]
    tgd = DataGeneratorLib(spark, number_of_generated_records)
    tgd_targets = DataGeneratorTarg(glueContext)
    generated_df = spark.range(0, number_of_generated_records, 1)
    generated_df = generated_df.withColumn("id", col("id").cast(StringType()))

    # Test Data Generation
    for atribute_config in config_file["attributes_list"]:
        fn = getattr(tgd, atribute_config["Generator"])
        generated_df = fn(
            generated_df,
            atribute_config["DataDescriptor"],
            atribute_config["ColumnName"],
        )

    generated_df = generated_df.drop("id")

    # Test Output writing

    for target_config in config_file["target_list"]:
        fn = getattr(tgd_targets, target_config["target"])
        fn(generated_df, target_config["attributes"])

    job.commit()


_main_test_data_generator()
