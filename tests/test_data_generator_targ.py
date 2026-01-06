import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Mock AWS Glue imports before any imports
sys.modules['awsglue'] = Mock()
sys.modules['awsglue.dynamicframe'] = Mock()

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Lib'))

from TestDataGeneratorTarg import DataGeneratorTarg


class TestTestDataGeneratorTarg(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_glue_context = Mock()
        self.tdg_targ = DataGeneratorTarg(self.mock_glue_context)
        
        # Mock DataFrame
        self.mock_df = Mock()
        self.mock_df.write.options.return_value.csv = Mock()
        
    def test_init(self):
        """Test DataGeneratorTarg initialization."""
        self.assertEqual(self.tdg_targ.glueContext, self.mock_glue_context)
        
    def test_s3_write(self):
        """Test S3 write functionality."""
        descriptor = {
            "header": True,
            "delimiter": ",",
            "BucketURI": "s3://test-bucket/path/",
            "mode": "overwrite"
        }
        
        # Mock the write chain
        mock_options = Mock()
        mock_csv = Mock()
        mock_options.csv = mock_csv
        self.mock_df.write.options.return_value = mock_options
        
        self.tdg_targ.S3(self.mock_df, descriptor)
        
        # Verify the write chain was called correctly
        self.mock_df.write.options.assert_called_once_with(
            header=descriptor["header"],
            delimiter=descriptor["delimiter"]
        )
        mock_csv.assert_called_once_with(
            descriptor["BucketURI"],
            mode=descriptor["mode"]
        )
        
    @patch('TestDataGeneratorTarg.DynamicFrame')
    def test_dynamodb_write(self, mock_dynamic_frame):
        """Test DynamoDB write functionality."""
        descriptor = {
            "dynamodb.output.tableName": "test-table",
            "dynamodb.throughput.write.percent": "0.5"
        }
        
        # Mock DynamicFrame
        mock_dyf = Mock()
        mock_dynamic_frame.fromDF.return_value = mock_dyf
        
        self.tdg_targ.Dynamodb(self.mock_df, descriptor)
        
        # Verify DynamicFrame creation
        mock_dynamic_frame.fromDF.assert_called_once_with(
            self.mock_df, 
            self.mock_glue_context, 
            "sample"
        )
        
        # Verify write_dynamic_frame_from_options call
        self.mock_glue_context.write_dynamic_frame_from_options.assert_called_once_with(
            frame=mock_dyf,
            connection_type="dynamodb",
            connection_options=descriptor
        )


if __name__ == '__main__':
    unittest.main()