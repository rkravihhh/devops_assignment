# Testing Documentation

This document provides information about the testing strategy for the Transaction Reconciliation API.

## Test Structure

The test suite consists of **pytest-based tests** covering all layers of the application:

### Test Categories
- **API Tests**: Test REST API endpoints with FastAPI TestClient
- **Service Tests**: Test business logic with mocked dependencies
- **Model Tests**: Test data validation and serialization

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# API tests only
pytest tests/test_api/

# Service tests only
pytest tests/test_services/

# Model tests only
pytest tests/test_models/
```

### Run Individual Test Files
```bash
pytest tests/test_main.py
pytest tests/test_transactions.py
pytest tests/test_issuers.py
```

### Run with Coverage
```bash
pytest --cov=app tests/
```

## Test Coverage

### API Tests
- `test_main.py` - Tests main application endpoints
- `test_transactions.py` - Tests transaction API endpoints
- `test_issuers.py` - Tests issuer API endpoints
- `test_reconciliations.py` - Tests reconciliation API endpoints

**Coverage**: All REST endpoints with various scenarios including:
- Successful requests
- Validation errors
- Resource not found errors
- Invalid input data
- Authentication and authorization

### Service Tests
- `test_transaction_service.py` - Tests transaction business logic
- `test_issuer_service.py` - Tests issuer management logic
- `test_reconciliation_service.py` - Tests reconciliation processing logic

**Coverage**: All business logic methods with:
- Happy path scenarios
- Exception handling
- Edge cases
- Data validation
- Background task processing

### Model Tests
- `test_schemas.py` - Tests Pydantic model validation
- `test_models.py` - Tests SQLAlchemy model relationships

**Coverage**: All data models with:
- Field validation
- Serialization/deserialization
- Database relationships
- Custom validators

## Test Configuration

### Mocking Strategy
- **Service Layer**: Mock database sessions to isolate business logic
- **API Layer**: Mock services to isolate endpoint testing
- **Database Layer**: Use test database or mocks for data operations

### Dependencies
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **httpx**: HTTP client for API testing
- **pytest-mock**: Mocking utilities

## Test Data Management

### Setup and Teardown
- Each test uses `pytest.fixture` for setup and teardown
- Mock objects created using `pytest-mock`
- Test data created using factory functions

### Test Data Factory Functions
Each test module includes helper functions to create test entities:
```python
def create_transaction_data(transaction_id: str, amount: float) -> dict:
    return {
        "transaction_id": transaction_id,
        "issuer_id": "ISSUER-001",
        "card_number": "4111111111111111",
        "amount": amount,
        "currency": "USD",
        "transaction_type": "purchase",
        "transaction_status": "completed",
        "transaction_date": "2024-01-01T10:00:00Z"
    }

def create_issuer_data(issuer_id: str, name: str) -> dict:
    return {
        "issuer_id": issuer_id,
        "issuer_name": name,
        "issuer_code": "TEST",
        "is_active": True
    }
```

## Assertions and Matchers

### Pytest Assertions
Used for standard assertions:
```python
assert response.status_code == 200
assert data["transaction_id"] == "TXN-001"
assert len(transactions) == 2
```

### FastAPI TestClient
Used for API endpoint testing:
```python
response = client.get("/api/v1/transactions/")
assert response.status_code == 200
data = response.json()
assert "transactions" in data
```

## Test Structure

```
tests/
├── test_main.py                    # Main application tests
├── test_transactions.py           # Transaction API tests
├── test_issuers.py               # Issuer API tests
├── test_reconciliations.py       # Reconciliation API tests
├── test_services/                # Service layer tests
│   ├── test_transaction_service.py
│   ├── test_issuer_service.py
│   └── test_reconciliation_service.py
└── test_models/                  # Model tests
    ├── test_schemas.py
    └── test_database_models.py
```

## Best Practices

### Test Naming
- Test functions use descriptive names: `test_create_transaction_success()`
- Test files follow pattern: `test_{module_name}.py`

### Test Organization
- Arrange-Act-Assert pattern used consistently
- Fixtures for common setup tasks
- Clear separation between test categories

### Error Testing
- Both positive and negative test cases
- Exception scenarios thoroughly tested
- Validation error responses verified

### Mocking
- Mock external dependencies only
- Use `pytest-mock` for mocking
- Verify interactions with mocked objects

## Performance Considerations

### Test Execution Speed
- Pure unit tests with mocked dependencies
- No database or external service calls
- Fast execution and immediate feedback

### Test Isolation
- Each test is completely independent
- No shared state between tests
- Fixtures provide clean test data

## Continuous Integration

### Pytest Commands
- `pytest` - Runs all tests
- `pytest -v` - Verbose output
- `pytest --cov=app` - Run with coverage
- `pytest tests/test_specific.py` - Run specific tests

### Test Reports
- Coverage reports generated with `pytest-cov`
- Test results integrated with CI/CD pipeline
- HTML coverage reports available

## Debugging Tests

### IDE Integration
- Run individual tests from IDE
- Debug tests with breakpoints
- View test execution results

### Logging
- Structured logging with request IDs
- Clear assertion failure messages
- Test execution logs available for troubleshooting