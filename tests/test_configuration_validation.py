import unittest
import os
from unittest.mock import patch, mock_open

# Mock yaml import
try:
    import yaml
except ImportError:
    from unittest.mock import Mock
    yaml = Mock()
    yaml.safe_load = Mock(return_value={})
    yaml.dump = Mock(return_value="")


class TestConfigurationValidation(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.valid_config = {
            "number_of_generated_records": 1000,
            "attributes_list": [
                {
                    "ColumnName": "PK",
                    "Generator": "key_generator",
                    "DataDescriptor": {
                        "Prefix": "PKey_",
                        "LeadingZeros": 7
                    }
                },
                {
                    "ColumnName": "ItemType",
                    "Generator": "string_generator",
                    "DataDescriptor": {
                        "Values": ["Electronic", "Mechanical", "Spare"]
                    }
                },
                {
                    "ColumnName": "ItemPrice",
                    "Generator": "float_generator",
                    "DataDescriptor": {
                        "Expression": "rand(42) * 3000"
                    }
                },
                {
                    "ColumnName": "InsertDate",
                    "Generator": "date_generator",
                    "DataDescriptor": {
                        "StartDate": "01/02/2001",
                        "EndDate": "01/03/2003"
                    }
                }
            ],
            "target_list": [
                {
                    "target": "S3",
                    "attributes": {
                        "BucketURI": "s3://test-bucket/path/",
                        "mode": "overwrite",
                        "header": "True",
                        "delimiter": ","
                    }
                }
            ]
        }
        
    def test_valid_configuration_structure(self):
        """Test that valid configuration has required structure."""
        self.assertIn("number_of_generated_records", self.valid_config)
        self.assertIn("attributes_list", self.valid_config)
        self.assertIn("target_list", self.valid_config)
        
        self.assertIsInstance(self.valid_config["number_of_generated_records"], int)
        self.assertIsInstance(self.valid_config["attributes_list"], list)
        self.assertIsInstance(self.valid_config["target_list"], list)
        
    def test_attribute_list_validation(self):
        """Test validation of attributes_list structure."""
        for attr in self.valid_config["attributes_list"]:
            self.assertIn("ColumnName", attr)
            self.assertIn("Generator", attr)
            self.assertIn("DataDescriptor", attr)
            
            self.assertIsInstance(attr["ColumnName"], str)
            self.assertIsInstance(attr["Generator"], str)
            self.assertIsInstance(attr["DataDescriptor"], dict)
            
    def test_supported_generators(self):
        """Test that all generators in config are supported."""
        supported_generators = [
            "key_generator",
            "child_key_generator", 
            "string_generator",
            "integer_generator",
            "float_generator",
            "date_generator",
            "close_date_generator",
            "ip_address_generator"
        ]
        
        for attr in self.valid_config["attributes_list"]:
            self.assertIn(attr["Generator"], supported_generators)
            
    def test_target_list_validation(self):
        """Test validation of target_list structure."""
        for target in self.valid_config["target_list"]:
            self.assertIn("target", target)
            self.assertIn("attributes", target)
            
            self.assertIsInstance(target["target"], str)
            self.assertIsInstance(target["attributes"], dict)
            
    def test_supported_targets(self):
        """Test that all targets in config are supported."""
        supported_targets = ["S3", "Dynamodb"]
        
        for target in self.valid_config["target_list"]:
            self.assertIn(target["target"], supported_targets)
            
    def test_s3_target_attributes(self):
        """Test S3 target attributes validation."""
        s3_targets = [t for t in self.valid_config["target_list"] if t["target"] == "S3"]
        
        for target in s3_targets:
            attrs = target["attributes"]
            self.assertIn("BucketURI", attrs)
            self.assertIn("mode", attrs)
            self.assertIn("header", attrs)
            self.assertIn("delimiter", attrs)
            
    def test_key_generator_descriptor(self):
        """Test key_generator DataDescriptor validation."""
        key_attrs = [a for a in self.valid_config["attributes_list"] 
                    if a["Generator"] == "key_generator"]
        
        for attr in key_attrs:
            desc = attr["DataDescriptor"]
            self.assertIn("LeadingZeros", desc)
            self.assertIsInstance(desc["LeadingZeros"], int)
            
            if "Prefix" in desc:
                self.assertIsInstance(desc["Prefix"], str)
                
    def test_string_generator_descriptor(self):
        """Test string_generator DataDescriptor validation."""
        string_attrs = [a for a in self.valid_config["attributes_list"] 
                       if a["Generator"] == "string_generator"]
        
        for attr in string_attrs:
            desc = attr["DataDescriptor"]
            
            # Should have one of: Values, Random+NumChar, or Pattern
            has_values = "Values" in desc
            has_random = "Random" in desc and "NumChar" in desc
            has_pattern = "Pattern" in desc
            
            self.assertTrue(has_values or has_random or has_pattern,
                          f"string_generator must have Values, Random+NumChar, or Pattern")
            
    def test_float_generator_descriptor(self):
        """Test float_generator DataDescriptor validation."""
        float_attrs = [a for a in self.valid_config["attributes_list"] 
                      if a["Generator"] == "float_generator"]
        
        for attr in float_attrs:
            desc = attr["DataDescriptor"]
            self.assertIn("Expression", desc)
            self.assertIsInstance(desc["Expression"], str)
            
    def test_date_generator_descriptor(self):
        """Test date_generator DataDescriptor validation."""
        date_attrs = [a for a in self.valid_config["attributes_list"] 
                     if a["Generator"] == "date_generator"]
        
        for attr in date_attrs:
            desc = attr["DataDescriptor"]
            self.assertIn("StartDate", desc)
            
            if "EndDate" in desc:
                # Validate date format
                start_date = desc["StartDate"]
                end_date = desc["EndDate"]
                self.assertRegex(start_date, r'\d{2}/\d{2}/\d{4}')
                self.assertRegex(end_date, r'\d{2}/\d{2}/\d{4}')
                
    def test_yaml_serialization(self):
        """Test that configuration can be serialized/deserialized as YAML."""
        yaml_str = yaml.dump(self.valid_config)
        loaded_config = yaml.safe_load(yaml_str)
        
        self.assertEqual(self.valid_config, loaded_config)
        
    def test_missing_required_fields(self):
        """Test validation fails for missing required fields."""
        # Test missing number_of_generated_records
        invalid_config = self.valid_config.copy()
        del invalid_config["number_of_generated_records"]
        
        with self.assertRaises(KeyError):
            self._validate_config_structure(invalid_config)
            
        # Test missing attributes_list
        invalid_config = self.valid_config.copy()
        del invalid_config["attributes_list"]
        
        with self.assertRaises(KeyError):
            self._validate_config_structure(invalid_config)
            
    def _validate_config_structure(self, config):
        """Helper method to validate configuration structure."""
        required_fields = ["number_of_generated_records", "attributes_list", "target_list"]
        for field in required_fields:
            if field not in config:
                raise KeyError(f"Missing required field: {field}")
        return True


if __name__ == '__main__':
    unittest.main()