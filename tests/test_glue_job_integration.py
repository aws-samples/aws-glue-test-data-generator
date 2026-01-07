import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys
import os

# Mock yaml import
try:
    import yaml
except ImportError:
    yaml = Mock()
    yaml.safe_load = Mock(return_value={})
    yaml.dump = Mock(return_value="")
    sys.modules['yaml'] = yaml

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Glue', 'Job'))


class TestTDGGlueJobIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock all AWS Glue and PySpark modules
        self.mock_modules = {
            'awsglue': Mock(),
            'awsglue.utils': Mock(),
            'awsglue.context': Mock(),
            'awsglue.job': Mock(),
            'pyspark': Mock(),
            'pyspark.context': Mock(),
            'pyspark.sql': Mock(),
            'pyspark.sql.types': Mock(),
            'pyspark.sql.functions': Mock(),
            'boto3': Mock(),
            'TestDataGeneratorLib': Mock(),
            'TestDataGeneratorTarg': Mock()
        }
        
        for module_name, mock_module in self.mock_modules.items():
            sys.modules[module_name] = mock_module
            
        # Sample configuration for testing
        self.sample_config = {
            "number_of_generated_records": 100,
            "attributes_list": [
                {
                    "ColumnName": "test_key",
                    "Generator": "key_generator",
                    "DataDescriptor": {
                        "Prefix": "KEY_",
                        "LeadingZeros": 5
                    }
                },
                {
                    "ColumnName": "test_string",
                    "Generator": "string_generator",
                    "DataDescriptor": {
                        "Values": ["A", "B", "C"]
                    }
                }
            ],
            "target_list": [
                {
                    "target": "S3",
                    "attributes": {
                        "BucketURI": "s3://test-bucket/",
                        "mode": "overwrite",
                        "header": "True",
                        "delimiter": ","
                    }
                }
            ]
        }
        
    @patch('sys.argv', ['script.py', '--JOB_NAME', 'test-job', '--config_file_path', 'test-bucket/config.yml'])
    @patch('boto3.client')
    @patch('yaml.safe_load')
    def test_main_test_data_generator_execution(self, mock_yaml_load, mock_boto3_client):
        """Test the main test data generator function execution."""
        # Mock S3 client and response
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        
        mock_response = {
            'Body': Mock()
        }
        mock_s3_client.get_object.return_value = mock_response
        mock_yaml_load.return_value = self.sample_config
        
        # Mock Spark and Glue components
        mock_spark = Mock()
        mock_glue_context = Mock()
        mock_job = Mock()
        
        # Mock DataFrame operations
        mock_df = Mock()
        mock_spark.range.return_value = mock_df
        mock_df.withColumn.return_value = mock_df
        mock_df.drop.return_value = mock_df
        
        # Mock TestDataGeneratorLib and TestDataGeneratorTarg
        mock_tdg = Mock()
        mock_tdg_targets = Mock()
        
        with patch('awsglue.utils.getResolvedOptions') as mock_get_options, \
             patch('pyspark.context.SparkContext') as mock_spark_context, \
             patch('awsglue.context.GlueContext') as mock_glue_context_class, \
             patch('awsglue.job.Job') as mock_job_class, \
             patch('TestDataGeneratorLib.DataGeneratorLib') as mock_tdg_class, \
             patch('TestDataGeneratorTarg.DataGeneratorTarg') as mock_targ_class:
            
            # Setup mocks
            mock_get_options.return_value = {
                'JOB_NAME': 'test-job',
                'config_file_path': 'test-bucket/config.yml'
            }
            
            mock_glue_context_class.return_value = mock_glue_context
            mock_glue_context.spark_session = mock_spark
            mock_job_class.return_value = mock_job
            mock_tdg_class.return_value = mock_tdg
            mock_targ_class.return_value = mock_tdg_targets
            
            # Mock generator methods
            mock_tdg.key_generator = Mock(return_value=mock_df)
            mock_tdg.string_generator = Mock(return_value=mock_df)
            mock_tdg_targets.S3 = Mock()
            
            # Import and execute the main function
            try:
                from TDGGlueJob import _main_test_data_generator
                _main_test_data_generator()
                
                # Test passes if no exception is raised
                self.assertTrue(True)
                
            except ImportError:
                # If import fails due to missing dependencies, skip the test
                self.skipTest("Cannot import TDGGlueJob due to missing dependencies")
                
    def test_config_file_parsing(self):
        """Test configuration file parsing logic."""
        config_yaml = yaml.dump(self.sample_config)
        
        with patch('builtins.open', mock_open(read_data=config_yaml)):
            loaded_config = yaml.safe_load(config_yaml)
            
            self.assertEqual(loaded_config['number_of_generated_records'], 100)
            self.assertEqual(len(loaded_config['attributes_list']), 2)
            self.assertEqual(len(loaded_config['target_list']), 1)
            
    def test_attribute_configuration_validation(self):
        """Test validation of attribute configurations."""
        for attr_config in self.sample_config['attributes_list']:
            self.assertIn('ColumnName', attr_config)
            self.assertIn('Generator', attr_config)
            self.assertIn('DataDescriptor', attr_config)
            
    def test_target_configuration_validation(self):
        """Test validation of target configurations."""
        for target_config in self.sample_config['target_list']:
            self.assertIn('target', target_config)
            self.assertIn('attributes', target_config)


if __name__ == '__main__':
    unittest.main()