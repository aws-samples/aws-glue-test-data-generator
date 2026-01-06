import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Mock PySpark imports before any imports
sys.modules['pyspark'] = Mock()
sys.modules['pyspark.sql'] = Mock()
sys.modules['pyspark.sql.functions'] = Mock()
sys.modules['pyspark.sql.types'] = Mock()
sys.modules['pyspark.context'] = Mock()

# Mock PySpark functions to return numeric values for arithmetic
from unittest.mock import Mock
mock_rand = Mock(return_value=0.5)
sys.modules['pyspark.sql.functions'].rand = mock_rand

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Lib'))

from TestDataGeneratorLib import DataGeneratorLib, helper_recursive_key_generator


class TestTestDataGeneratorLib(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_spark = Mock()
        self.number_of_records = 100
        self.tdg = DataGeneratorLib(self.mock_spark, self.number_of_records)
        
        # Mock DataFrame
        self.mock_df = Mock()
        self.mock_df.withColumn.return_value = self.mock_df
        self.mock_df.drop.return_value = self.mock_df
        self.mock_df.join.return_value = self.mock_df
        
    def test_init(self):
        """Test DataGeneratorLib initialization."""
        self.assertEqual(self.tdg.spark, self.mock_spark)
        self.assertEqual(self.tdg.number_of_generated_records, self.number_of_records)
        self.assertEqual(self.tdg.random_seed, 52)
        
    def test_string_generator_with_values(self):
        """Test string_generator with predefined values."""
        descriptor = {
            "Values": ["value1", "value2", "value3"]
        }
        column_name = "test_column"
        
        # Mock createDataFrame
        mock_lookup_df = Mock()
        self.mock_spark.createDataFrame.return_value = mock_lookup_df
        
        result = self.tdg.string_generator(self.mock_df, descriptor, column_name)
        
        self.mock_spark.createDataFrame.assert_called_once()
        self.assertIsNotNone(result)
        
    def test_string_generator_with_random(self):
        """Test string_generator with random strings."""
        descriptor = {
            "Random": "True",
            "NumChar": 10
        }
        column_name = "test_column"
        
        result = self.tdg.string_generator(self.mock_df, descriptor, column_name)
        
        self.assertIsNotNone(result)
        
    def test_string_generator_with_pattern(self):
        """Test string_generator with pattern."""
        descriptor = {
            "Pattern": "Test#^X5#_#^N3"
        }
        column_name = "test_column"
        
        result = self.tdg.string_generator(self.mock_df, descriptor, column_name)
        
        self.assertIsNotNone(result)
        
    def test_key_generator_with_prefix(self):
        """Test key_generator with prefix."""
        descriptor = {
            "Prefix": "KEY_",
            "LeadingZeros": 5
        }
        column_name = "test_key"
        
        result = self.tdg.key_generator(self.mock_df, descriptor, column_name)
        
        self.assertIsNotNone(result)
        
    def test_key_generator_without_prefix(self):
        """Test key_generator without prefix."""
        descriptor = {
            "LeadingZeros": 5
        }
        column_name = "test_key"
        
        result = self.tdg.key_generator(self.mock_df, descriptor, column_name)
        
        self.assertIsNotNone(result)
        
    def test_integer_generator(self):
        """Test integer_generator."""
        descriptor = {
            "Range": "1,100"
        }
        column_name = "test_int"
        
        result = self.tdg.integer_generator(self.mock_df, descriptor, column_name)
        
        self.assertIsNotNone(result)
        
    def test_integer_generator_with_seed(self):
        """Test integer_generator with custom seed."""
        descriptor = {
            "Range": "1,100",
            "Seed": "42"
        }
        column_name = "test_int"
        
        result = self.tdg.integer_generator(self.mock_df, descriptor, column_name)
        
        self.assertIsNotNone(result)
        
    def test_float_generator(self):
        """Test float_generator."""
        descriptor = {
            "Expression": "rand(42) * 1000"
        }
        column_name = "test_float"
        
        result = self.tdg.float_generator(self.mock_df, descriptor, column_name)
        
        self.assertIsNotNone(result)
        
    def test_date_generator(self):
        """Test date_generator."""
        descriptor = {
            "StartDate": "01/01/2020",
            "EndDate": "31/12/2020"
        }
        column_name = "test_date"
        
        result = self.tdg.date_generator(self.mock_df, descriptor, column_name)
        
        self.assertIsNotNone(result)
        
    def test_close_date_generator(self):
        """Test close_date_generator."""
        descriptor = {
            "StartDateColumnName": "start_date",
            "CloseDateRangeInDays": "30"
        }
        column_name = "close_date"
        
        result = self.tdg.close_date_generator(self.mock_df, descriptor, column_name)
        
        self.assertIsNotNone(result)
        
    def test_ip_address_generator(self):
        """Test ip_address_generator."""
        descriptor = {
            "IpRanges": ["1,10", "1,255", "1,255", "1,255"]
        }
        column_name = "ip_address"
        
        result = self.tdg.ip_address_generator(self.mock_df, descriptor, column_name)
        
        self.assertIsNotNone(result)
        
    def test_ip_address_generator_default_ranges(self):
        """Test ip_address_generator with default ranges."""
        descriptor = {}
        column_name = "ip_address"
        
        result = self.tdg.ip_address_generator(self.mock_df, descriptor, column_name)
        
        self.assertIsNotNone(result)


class TestHelperFunctions(unittest.TestCase):
    
    def setUp(self):
        """Reset global variables before each test."""
        import TestDataGeneratorLib
        TestDataGeneratorLib.tmp_id_global_counter = 0
        TestDataGeneratorLib.generated_keys_list = []
        
    def test_helper_recursive_key_generator(self):
        """Test helper_recursive_key_generator function."""
        sublevel_children_number_list = [2, 3]
        number_of_generated_records = 10
        
        helper_recursive_key_generator(0, 0, sublevel_children_number_list, number_of_generated_records)
        
        import TestDataGeneratorLib
        self.assertGreater(len(TestDataGeneratorLib.generated_keys_list), 0)
        self.assertLessEqual(TestDataGeneratorLib.tmp_id_global_counter, number_of_generated_records)


if __name__ == '__main__':
    unittest.main()