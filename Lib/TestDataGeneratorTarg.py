from awsglue.dynamicframe import DynamicFrame

class TestDataGeneratorTarg:
    def __init__(self,glueContext):
        self.glueContext = glueContext

    def S3(self,df,descriptor):
        df.write.options(header=descriptor['header'], delimiter=descriptor['delimiter']).csv(descriptor['BucketArn'],mode=descriptor['mode'])
        
    def Dynamodb(self,df,descriptor):
        dyf = DynamicFrame.fromDF(df,self.glueContext,"sample")
        self.glueContext.write_dynamic_frame_from_options(
            frame=dyf,
            connection_type="dynamodb",
            connection_options=descriptor
        )