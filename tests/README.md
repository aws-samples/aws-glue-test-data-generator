# Unit Tests for AWS Glue Test Data Generator

This directory contains comprehensive unit tests for the AWS Glue Test Data Generator project.

## Test Structure

- `test_data_generator_lib.py` - Tests for the main TestDataGeneratorLib class
- `test_data_generator_targ.py` - Tests for the TestDataGeneratorTarg class  
- `test_glue_job_integration.py` - Integration tests for the main Glue job
- `test_configuration_validation.py` - Tests for configuration file validation
- `run_tests.py` - Test runner script

## Running Tests

### Using the test runner script:
```bash
python tests/run_tests.py
```

### Using pytest (recommended):
```bash
# Install test dependencies
pip install -r test-requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=Lib --cov=Glue

# Run specific test file
pytest tests/test_data_generator_lib.py

# Run with verbose output
pytest -v
```

### Using unittest:
```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_data_generator_lib
```

## Test Categories

- **Unit Tests**: Test individual methods and functions in isolation
- **Integration Tests**: Test the interaction between components
- **Configuration Tests**: Validate YAML configuration files

## Mocking Strategy

The tests use extensive mocking to avoid dependencies on:
- PySpark/Spark Session
- AWS Glue Context
- AWS SDK (boto3)
- External services (S3, DynamoDB)

This allows tests to run in any environment without requiring AWS credentials or Spark installation.

## Test Coverage

The tests cover:
- All data generator methods (string, key, integer, float, date, IP address)
- Target writers (S3, DynamoDB)
- Configuration validation
- Error handling
- Edge cases and boundary conditions