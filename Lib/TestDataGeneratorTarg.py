from awsglue.dynamicframe import DynamicFrame

class TestDataGeneratorTarg:
    """
    A class that provides methods to write data to different data storage services, such as S3 and DynamoDB, using the GlueContext provided.

    Attributes:
        glueContext: The GlueContext object used for interacting with AWS Glue services.

    Methods:
        S3(df, descriptor):
            Write the given DataFrame to an S3 bucket with the specified options.

        Dynamodb(df, descriptor):
            Write the given DataFrame to a DynamoDB table using the provided connection options.
    """
    
    def __init__(self,glueContext):
        """
        Initialize the TestDataGeneratorTarg object with the GlueContext.

        Parameters:
            glueContext (GlueContext): The GlueContext object used for interacting with AWS Glue services.
        """
        self.glueContext = glueContext

    def S3(self,df,descriptor):
        """
        Write the given DataFrame to an S3 bucket with the specified options.

        Parameters:
            df (DataFrame): The DataFrame to be written to the S3 bucket.
            descriptor (dict): A dictionary containing the options for writing to S3.
                - 'header' (bool): Whether to include a header row in the CSV file.
                - 'delimiter' (str): The delimiter to be used in the CSV file.
                - 'BucketArn' (str): The ARN (Amazon Resource Name) of the target S3 bucket.
                - 'mode' (str): The write mode, e.g., 'overwrite' or 'append'.

        Note:
            The DataFrame will be written as a CSV file to the specified S3 bucket.
        """
        df.write.options(header=descriptor['header'], delimiter=descriptor['delimiter']).csv(descriptor['BucketArn'],mode=descriptor['mode'])
        
    def Dynamodb(self,df,descriptor):
        """
        Write the given DataFrame to a DynamoDB table using the provided connection options.

        Parameters:
            df (DataFrame): The DataFrame to be written to the DynamoDB table.
            descriptor (dict): A dictionary containing the connection options for writing to DynamoDB.
                - 'dynamodb.output.tableName' (str): The name of the target DynamoDB table.
        Note:
            The DataFrame will be converted to a DynamicFrame before writing to DynamoDB.
            The connection options must be specified as per the AWS Glue write_dynamic_frame_from_options method.
        """
        dyf = DynamicFrame.fromDF(df,self.glueContext,"sample")
        self.glueContext.write_dynamic_frame_from_options(
            frame=dyf,
            connection_type="dynamodb",
            connection_options=descriptor
        )
