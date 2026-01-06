import unittest
from unittest.mock import Mock
import sys
import os

# Mock PySpark before importing
sys.modules['pyspark'] = Mock()
sys.modules['pyspark.sql'] = Mock()
sys.modules['pyspark.sql.functions'] = Mock()
sys.modules['pyspark.sql.types'] = Mock()
sys.modules['pyspark.context'] = Mock()

# Mock rand function to return numeric value
mock_rand = Mock(return_value=0.5)
sys.modules['pyspark.sql.functions'].rand = mock_rand

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Lib'))
from TestDataGeneratorLib import DataGeneratorLib


class TestBasicFunctionality(unittest.TestCase):
    
    def setUp(self):
        self.mock_spark = Mock()
        self.tdg = DataGeneratorLib(self.mock_spark, 100)
        self.mock_df = Mock()
        self.mock_df.withColumn.return_value = self.mock_df
        
    def test_initialization(self):
        """Test basic initialization works."""
        self.assertEqual(self.tdg.number_of_generated_records, 100)
        self.assertEqual(self.tdg.random_seed, 52)
        
    def test_key_generator(self):
        """Test key generator works without errors."""
        descriptor = {"Prefix": "KEY_", "LeadingZeros": 5}
        result = self.tdg.key_generator(self.mock_df, descriptor, "test_key")
        self.assertIsNotNone(result)
        
    def test_integer_generator(self):
        """Test integer generator works without errors."""
        descriptor = {"Range": "1,100"}
        result = self.tdg.integer_generator(self.mock_df, descriptor, "test_int")
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()