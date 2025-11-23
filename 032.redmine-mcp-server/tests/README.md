# Redmine MCP Server Tests

This directory contains the test suite for the Redmine MCP Server project, organized for pytest and coverage measurement.

## Test Structure

### Unit Tests
- `test_mcp_server_unit.py` - Unit tests for the MCP server functionality
- `test_selenium_unit.py` - Unit tests for the Selenium scraper functionality
- `conftest.py` - Pytest configuration and shared fixtures

### Integration Tests
- `test_integration.py` - Integration tests that require a running Redmine instance

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r scripts/requirements.txt
```

### Quick Start

Run all tests with coverage:
```bash
python run_tests.py
```

### Manual Test Execution

#### Unit Tests Only
```bash
pytest -v -m "not integration" tests/
```

#### Unit Tests with Coverage
```bash
pytest --cov=src --cov-report=html --cov-report=term-missing -v -m "not integration" tests/
```

#### Integration Tests
```bash
pytest -v -m integration tests/
```

#### All Tests
```bash
pytest -v tests/
```

## Test Categories

### Unit Tests (`-m "not integration"`)
- Fast execution
- No external dependencies
- Mock all external services
- Test individual functions and methods

### Integration Tests (`-m integration`)
- Require running Redmine instance
- Need valid credentials in environment variables
- Test end-to-end functionality
- May require manual intervention (2FA)

## Coverage Reports

Coverage reports are generated in multiple formats:
- **Terminal**: Shows missing lines during test run
- **HTML**: Detailed report in `htmlcov/index.html`
- **XML**: Machine-readable format in `coverage.xml`

## Environment Variables for Integration Tests

Set these environment variables to run integration tests:

```bash
REDMINE_URL=http://your-redmine-instance.com
REDMINE_USERNAME=your-username
REDMINE_PASSWORD=your-password
```

## Test Markers

- `@pytest.mark.unit` - Unit tests (default)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Tests that take a long time
- `@pytest.mark.asyncio` - Async tests

## Fixtures

Common fixtures are defined in `conftest.py`:
- `mock_scraper` - Mock RedmineSeleniumScraper
- `mock_config` - Mock configuration

## Best Practices

1. **Unit tests should be fast** - Use mocks for external dependencies
2. **Integration tests should be realistic** - Test against real Redmine instance
3. **Use descriptive test names** - Clearly indicate what is being tested
4. **Group related tests** - Use test classes to organize related functionality
5. **Mock external dependencies** - Don't rely on network calls in unit tests

## Continuous Integration

For CI/CD pipelines, run only unit tests:
```bash
pytest --cov=src --cov-report=xml -m "not integration" tests/
```

Integration tests should be run separately with proper Redmine instance setup.