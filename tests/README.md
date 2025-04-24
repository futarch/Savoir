# R2R API Tests

This directory contains tests for the R2R API integration. The tests verify that the API is being called correctly from the different functions in the R2R folder.

## Test Files

- `test_r2r_api.py`: Tests for the high-level API functions in the R2R folder
- `test_r2r_client.py`: Tests for the R2R client that makes the actual API calls
- `test_r2r_errors.py`: Tests for error handling in the R2R integration
- `test_r2r_utils.py`: Tests for utility functions used by the R2R integration
- `run_r2r_tests.py`: Script to run all R2R tests

## Running the Tests

You can run all the tests using the provided script:

```bash
./run_r2r_tests.py
```

Or you can run individual test files using pytest:

```bash
pytest test_r2r_api.py -v
pytest test_r2r_client.py -v
pytest test_r2r_errors.py -v
pytest test_r2r_utils.py -v
```

## Test Coverage

The tests cover the following functionality:

1. **Document Operations**
   - Creating documents
   - Adding documents to collections
   - Adding documents to multiple collections

2. **Collection Operations**
   - Creating collections
   - Listing collections

3. **Search Operations**
   - Searching with collection names
   - RAG (Retrieval-Augmented Generation) with collection names

4. **Error Handling**
   - Error responses from the API
   - Validation errors
   - Network errors

5. **Utility Functions**
   - Waiting for resources to be ready
   - Making API requests
   - Formatting responses
   - Validating collection names

## Mocking

The tests use mocking to avoid making actual API calls during testing. This ensures that the tests are fast and reliable, and don't depend on external services.

## Requirements

To run the tests, you need:

- Python 3.7+
- pytest
- pytest-asyncio
- aiohttp

You can install the requirements using pip:

```bash
pip install pytest pytest-asyncio aiohttp
``` 