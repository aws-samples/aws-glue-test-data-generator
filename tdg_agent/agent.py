from strands import Agent, tool
from strands.models import BedrockModel
import boto3
from bedrock_agentcore.runtime import BedrockAgentCoreApp


app = BedrockAgentCoreApp()

@tool
def invoke_tdg_glue_job(job_name: str = "TestDataGeneratorJob", config_yaml: str = None) -> str:
    """
    The AWS Glue Test Data Generator provides a configurable framework for Test Data Generation using AWS Glue Pyspark serverless Jobs. The required test data description is fully configurable through a YAML configuration file.
    
    Supported data types:
    - Unique Key Generator: formatted unique values with prefix and leading zeros
    - Child Key Generator: hierarchical keys for multi-level data
    - String Data Generator: random strings, dictionary values, or pattern-based
    - Integer Data Generator: random integers from specified range
    - Float/Double Data Generator: random floats from SQL expressions
    - Date Data Generator: random dates from configurable range
    - Close Date Data Generator: dates relative to other date columns
    - Internet Address Data Generator: random IP addresses
    - JSON Data Generator: JSON documents with arrays, nested objects, and configurable fields
    
    Target outputs:
    - S3 Buckets: CSV or Parquet format
    - DynamoDB tables: with configurable throughput
    
    Configuration YAML format:

    number_of_generated_records: 1000
    attributes_list:
      - ColumnName: PK
        Generator: key_generator
        DataDescriptor:
          Prefix: PKey_
          LeadingZeros: 7
      - ColumnName: SK
        Generator: string_generator
        DataDescriptor:
          Pattern: SKey_#^X10
      - ColumnName: ParentItemId
        Generator: child_key_generator
        DataDescriptor:
          Prefix: PKey_
          LeadingZeros: 7
          ChildCountPerSublevel:
            - 10
            - 100
            - 1000
      - ColumnName: ItemType
        Generator: string_generator
        DataDescriptor:
          Values:
            - Elecotronic Part
            - Mechnical Part
            - Spare Part
            - Harness
            - Accessory
      - ColumnName: ItemPrice
        Generator: float_generator
        DataDescriptor:
          Expression: rand(42) * 3000
      - ColumnName: Status
        Generator: string_generator
        DataDescriptor:
          Values:
            - OUT_OF_STOCK
            - AVAILABLE
            - ORDERED
            - RETIRED
      - ColumnName: PartNumber
        Generator: string_generator
        DataDescriptor:
          Pattern: Part_#^A10
      - ColumnName: SerialNumber
        Generator: string_generator
        DataDescriptor:
          Random: 'True'
          NumChar: 16
      - ColumnName: ItemDetails
        Generator: string_generator
        DataDescriptor:
          Pattern: "Contact Details: Email: #^X8#__#^N2#@#^A4#.#^A3# Phone: #^N8"
      - ColumnName: InsertDate
        Generator: date_generator
        DataDescriptor:
          StartDate: 01/02/2001
          EndDate: 01/03/2003
      - ColumnName: ExpireDate
        Generator: close_date_generator
        DataDescriptor:
          StartDateColumnName: InsertDate
          CloseDateRangeInDays: 365
      - ColumnName: internet_adress
        Generator: ip_address_generator
        DataDescriptor:
          IpRanges: 
            - 9,10
            - 1,254
            - 1,128
            - 2,20
      - ColumnName: user_profile
        Generator: json_generator
        DataDescriptor:
          Schema:
            user_id: "USR001"
            name: "John Doe"
            email: "john.doe@example.com"
            age: 25
            balance: 1500.50
            status: "active"
            tags: ["premium", "verified"]
            address:
              street: "123 Main St"
              city: "New York"
              zip: 10001
            orders:
              - order_id: "ORD001"
                amount: 99.99
              - order_id: "ORD002"
                amount: 149.50
            contacts:
              - type: "email"
                value: "john@example.com"
                verified: true
              - type: "phone"
                value: "+1234567890"
                verified: false
          FieldConfigs:
            user_id:
              Generator: key_generator
              DataDescriptor:
                Prefix: "USR"
                LeadingZeros: 6
            name:
              Generator: string_generator
              DataDescriptor:
                Values:
                  - "John Smith"
                  - "Jane Doe"
                  - "Mike Johnson"
            age:
              Generator: integer_generator
              DataDescriptor:
                Range: "18,65"
            status:
              Generator: string_generator
              DataDescriptor:
                Values:
                  - "active"
                  - "inactive"
                  - "suspended"
    target_list:
      - target: Dynamodb
        attributes:
          dynamodb.output.tableName: test-json
          dynamodb.throughput.write.percent: 0.5
      - target: S3
        attributes:
          BucketURI: s3://tdg-target-bucket/generated_dataset/
          mode: overwrite
          header: 'True'
          delimiter: ','

      sample  of the expected output:
PK,SK,ParentItemId,ItemType,ItemPrice,Status,PartNumber,SerialNumber,ItemDetails,InsertDate,ExpireDate,internet_adress,user_profile
PKey_0000006,SKey_Kxsmhjay2O,PKey_0000002,Elecotronic Part,1528.8057,AVAILABLE,Part_WbNmxkYOUq,vprdZ8uzNbml05j,Contact Details: Email: yglGdIh2__7@deQ.Dpv Phone: 26715308,2001-08-24,2001-11-30,10.73.86.3,"{\"user_id\":\"USR000006\",\"name\":\"John Smith\",\"email\":\"john.doe@example.com\",\"age\":49,\"balance\":1500.5,\"status\":\"inactive\"}"
PKey_0000009,SKey_DYMHGPS6Ro,PKey_0000002,Elecotronic Part,2497.578,OUT_OF_STOCK,Part_FnmJHPhgIx,wpqb7Qd3V206L8J,Contact Details: Email: j0eMaFk8__62@oLNv.HkF Phone: 2817943,2001-04-22,2001-05-30,9.126.121.4,"{\"user_id\":\"USR000009\",\"name\":\"John Smith\",\"email\":\"john.doe@example.com\",\"age\":30,\"balance\":1500.5,\"status\":\"active\"}"
PKey_0000041,SKey_CJQLOdRS7,PKey_0000002,Elecotronic Part,2997.4324,OUT_OF_STOCK,Part_cbSBQFqXw,4pX7eomnZf6HCYBV,Contact Details: Email: sM6UbhwC__52@Bhuw.FYp Phone: 1836027,2001-02-02,2001-02-02,9.115.109.9,"{\"user_id\":\"USR000041\",\"name\":\"John Smith\",\"email\":\"john.doe@example.com\",\"age\":23,\"balance\":1500.5,\"status\":\"active\"}"
PKey_0000048,SKey_8XL7fsiYb2,PKey_0000002,Elecotronic Part,2387.8728,OUT_OF_STOCK,Part_ApSYrQeyNt,pvSILliZtUKujmYR,Contact Details: Email: oalTD4Yq__67@PYg.wNq Phone: 7846519,2001-05-11,2001-06-28,10.4.101.14,"{\"user_id\":\"USR000048\",\"name\":\"John Smith\",\"email\":\"john.doe@example.com\",\"age\":34,\"balance\":1500.5,\"status\":\"inactive\"}"
PKey_0000086,SKey_Wkoabwf5EQ,PKey_0000002,Elecotronic Part,2497.8284,OUT_OF_STOCK,Part_lTqfUtAFGW,C9ktgAl7PTBcEJ3U,Contact Details: Email: JqAsmU8r__95@KUXz.oUq Phone: 1943825,2001-04-01,2001-04-29,10.40.123.10,"{\"user_id\":\"USR000086\",\"name\":\"John Smith\",\"email\":\"john.doe@example.com\",\"age\":51,\"balance\":1500.5,\"status\":\"suspended\"}"

    Args:
        job_name (str): Name of the Glue job to run (default: TestDataGeneratorJob)
        config_yaml (str): Optional YAML configuration as string. If not provided, uses S3 config.
        
    Returns:
        str: Job run ID and status
    """
    try:
        glue_client = boto3.client('glue')
        
        job_args = {}
        if config_yaml:
            job_args['--config_yaml'] = config_yaml
            
        response = glue_client.start_job_run(
            JobName=job_name,
            Arguments=job_args
        )
        job_run_id = response['JobRunId']
        
        config_source = "provided YAML config" if config_yaml else "S3 config file"
        return f"Successfully started Glue job '{job_name}' with run ID: {job_run_id} using {config_source}"
    except Exception as e:
        return f"Error starting Glue job: {str(e)}"

@tool
def get_tdg_glue_job_status(job_name: str = "TestDataGeneratorJob", job_run_id: str = None) -> str:
    """
    Get the status of an AWS Glue Test Data Generator job run.
    
    Args:
        job_name (str): Name of the Glue job (default: TestDataGeneratorJob)
        job_run_id (str): Optional specific job run ID. If not provided, gets the latest run.
        
    Returns:
        str: Job status information including state, progress, and execution details
    """
    try:
        glue_client = boto3.client('glue')
        
        if job_run_id:
            # Get specific job run
            response = glue_client.get_job_run(
                JobName=job_name,
                RunId=job_run_id
            )
            job_run = response['JobRun']
        else:
            # Get latest job run
            response = glue_client.get_job_runs(
                JobName=job_name,
                MaxResults=1
            )
            if not response['JobRuns']:
                return f"No job runs found for job '{job_name}'"
            job_run = response['JobRuns'][0]
        
        status = job_run['JobRunState']
        run_id = job_run['Id']
        started_on = job_run.get('StartedOn', 'N/A')
        completed_on = job_run.get('CompletedOn', 'N/A')
        execution_time = job_run.get('ExecutionTime', 0)
        
        status_info = f"Job: {job_name}\n"
        status_info += f"Run ID: {run_id}\n"
        status_info += f"Status: {status}\n"
        status_info += f"Started: {started_on}\n"
        
        if status in ['SUCCEEDED', 'FAILED', 'STOPPED']:
            status_info += f"Completed: {completed_on}\n"
            status_info += f"Execution Time: {execution_time} seconds\n"
        
        if status == 'FAILED':
            error_message = job_run.get('ErrorMessage', 'No error details available')
            status_info += f"Error: {error_message}\n"
        
        return status_info
        
    except Exception as e:
        return f"Error getting job status: {str(e)}"

# Define model and agent
model_id = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
model = BedrockModel(
    model_id=model_id,
)


agent = Agent(
    model=model,
    tools=[invoke_tdg_glue_job, get_tdg_glue_job_status],
    system_prompt="you are an technical consultant who generates test data. to help user, you need to print all parameters you use while invoking the tools"
)

# Entrypoint for AgentCore Runtime
@app.entrypoint
def invoke(payload):
    user_input = payload.get("prompt")
    response = agent(user_input)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run()