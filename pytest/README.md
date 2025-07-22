# Audio Processing System - Test Suite

A comprehensive pytest testing suite for the Simple Audio Processing System, designed to ensure robust, scalable, and secure audio processing capabilities.

## 📋 Overview

This test suite covers:
- **Unit Tests**: Individual component testing
- **Functional Tests**: End-to-end workflow testing
- **Performance Tests**: Load and performance validation
- **Security Tests**: Security vulnerability testing

## 🗂️ Directory Structure

```
pytest/
├── conftest.py                 # Shared fixtures and configuration
├── pytest.ini                 # Pytest configuration
├── requirements.txt            # Testing dependencies
├── README.md                  # This documentation
├── utils/
│   └── test_helpers.py        # Test utility functions
├── unit_tests/
│   ├── test_algorithms.py     # Algorithm A & B unit tests
│   └── test_message_broker.py # RabbitMQ unit tests
├── functional_tests/
│   └── test_end_to_end.py     # Integration and E2E tests
├── performance_tests/
│   └── test_load_performance.py # Performance and load tests
└── security_tests/
    └── test_security.py       # Security and vulnerability tests
```

## 🚀 Quick Start

### Installation

```bash
# Install test dependencies
pip install -r requirements.txt

# Install the system under test (adjust path as needed)
pip install -e ../
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit                 # Unit tests only
pytest -m functional          # Functional tests only
pytest -m performance         # Performance tests only
pytest -m security            # Security tests only

# Run tests with coverage
pytest --cov=audio_processing --cov-report=html

# Run tests in parallel
pytest -n auto
```

## 📊 Test Categories

### Unit Tests (`-m unit`)
**Purpose**: Test individual components in isolation
**Coverage**:
- Algorithm A audio processing
- Algorithm B feature enhancement
- RabbitMQ message broker operations
- Database operations
- API endpoints

**Example**:
```bash
pytest unit_tests/test_algorithms.py::TestAlgorithmA::test_audio_validation -v
```

### Functional Tests (`-m functional`)
**Purpose**: Test complete workflows and integration points
**Coverage**:
- End-to-end audio processing pipeline
- Sensor → RabbitMQ → Algorithms → Database → API
- Load balancing across algorithm pods
- Data consistency validation
- System resilience testing

**Example**:
```bash
pytest functional_tests/test_end_to_end.py::TestEndToEndAudioProcessing::test_complete_audio_pipeline -v
```

### Performance Tests (`-m performance`)
**Purpose**: Validate system performance under various loads
**Coverage**:
- Algorithm processing time benchmarks
- Message broker throughput testing
- Database read/write performance
- API response time under load
- Memory usage and CPU utilization
- Sustained load testing

**Example**:
```bash
pytest performance_tests/test_load_performance.py::TestSystemLoadTesting::test_sustained_load -v
```

### Security Tests (`-m security`)
**Purpose**: Identify and prevent security vulnerabilities
**Coverage**:
- Authentication and authorization
- Input validation and sanitization
- SQL injection prevention
- XSS and CSRF protection
- Data encryption testing
- Network security validation

**Example**:
```bash
pytest security_tests/test_security.py::TestAuthenticationSecurity::test_jwt_token_validation -v
```

## 🎯 Test Execution Strategies

### Development Testing
```bash
# Quick feedback during development
pytest -m unit --tb=short --durations=5

# Test specific component
pytest unit_tests/test_algorithms.py -v
```

### Pre-commit Testing
```bash
# Fast, essential tests
pytest -m "unit and not slow" --maxfail=5
```

### CI/CD Pipeline Testing
```bash
# Comprehensive testing with reporting
pytest --cov=. --cov-report=xml --junit-xml=test_results.xml -m "not slow"

# Performance baseline testing
pytest -m performance --benchmark-save=baseline
```

### Manual QA Testing
```bash
# Complete test suite including slow tests
pytest -m "functional or integration" --durations=10

# Security audit
pytest -m security --tb=long
```

## 📈 Performance Benchmarks

### Expected Performance Thresholds

| Component | Metric | Threshold |
|-----------|--------|-----------|
| Algorithm A | Processing Time | < 200ms avg |
| Algorithm B | Processing Time | < 150ms avg |
| Message Broker | Throughput | > 500 msg/s |
| Database Write | Latency | < 10ms per record |
| API Response | Time | < 500ms |
| Memory Usage | Growth | < 50MB over 1000 ops |

### Running Performance Tests
```bash
# Basic performance testing
pytest -m performance

# Extended load testing (takes longer)
pytest -m "performance and slow"

# Performance with profiling
pytest -m performance --profile
```

## 🔒 Security Testing

### Security Test Categories

1. **Authentication & Authorization**
   - JWT token validation
   - Role-based access control
   - API rate limiting

2. **Input Validation**
   - JSON payload validation
   - SQL injection prevention
   - Command injection prevention
   - XXE attack prevention

3. **Data Protection**
   - Audio data encryption
   - Sensitive data masking
   - Database encryption at rest

4. **Network Security**
   - TLS certificate validation
   - Secure RabbitMQ connections
   - Network traffic filtering

5. **Vulnerability Testing**
   - XSS prevention
   - CSRF protection
   - Directory traversal prevention
   - Insecure deserialization prevention

### Running Security Tests
```bash
# Complete security audit
pytest -m security --tb=long

# Specific security category
pytest security_tests/test_security.py::TestInputValidationSecurity -v
```

## 📋 Test Configuration

### Environment Variables
```bash
# Test database configuration
export TEST_DB_URL="postgresql://test:test@localhost:5432/test_db"

# Test RabbitMQ configuration
export TEST_RABBITMQ_URL="amqp://test:test@localhost:5672/"

# Test Redis configuration
export TEST_REDIS_URL="redis://localhost:6379/1"

# Enable debug logging
export TEST_LOG_LEVEL="DEBUG"
```

### Custom Pytest Markers
```bash
# Run only fast tests
pytest -m "not slow"

# Run integration tests
pytest -m "functional or integration"

# Run performance-critical tests
pytest -m "performance and not slow"
```

## 🛠️ Test Development Guidelines

### Writing New Tests

1. **Follow naming conventions**:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test methods: `test_*`

2. **Use appropriate markers**:
   ```python
   @pytest.mark.unit
   @pytest.mark.asyncio
   async def test_my_function():
       pass
   ```

3. **Leverage fixtures**:
   ```python
   def test_audio_processing(sample_audio_data, mock_rabbitmq_connection):
       # Test implementation
       pass
   ```

4. **Use helper utilities**:
   ```python
   from utils.test_helpers import AudioDataGenerator, PerformanceTracker
   ```

### Best Practices

- **Isolation**: Each test should be independent
- **Mocking**: Use mocks for external dependencies
- **Assertions**: Clear, specific assertions with helpful messages
- **Documentation**: Document complex test scenarios
- **Performance**: Consider test execution time
- **Cleanup**: Properly clean up resources

## 📊 Test Reporting

### Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Terminal coverage report
pytest --cov=. --cov-report=term-missing
```

### Performance Reports
```bash
# Generate performance baseline
pytest -m performance --benchmark-save=baseline

# Compare against baseline
pytest -m performance --benchmark-compare=baseline
```

### CI/CD Integration

Example GitHub Actions workflow:
```yaml
- name: Run Unit Tests
  run: pytest -m unit --cov=. --cov-report=xml

- name: Run Security Tests
  run: pytest -m security --tb=short

- name: Upload Coverage
  uses: codecov/codecov-action@v1
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Ensure system is installed
   pip install -e ../
   ```

2. **Database Connection Issues**:
   ```bash
   # Start test database
   docker run -d -p 5432:5432 -e POSTGRES_DB=test_db postgres:13
   ```

3. **RabbitMQ Connection Issues**:
   ```bash
   # Start test RabbitMQ
   docker run -d -p 5672:5672 rabbitmq:3.9
   ```

4. **Async Test Issues**:
   ```python
   # Ensure pytest-asyncio is installed and configured
   pip install pytest-asyncio
   ```

### Debug Mode
```bash
# Run with debug output
pytest -v -s --tb=long --log-cli-level=DEBUG
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [System Architecture Documentation](../docs/architecture.md)

## 🤝 Contributing

1. Add tests for new features
2. Ensure all tests pass: `pytest`
3. Maintain test coverage above 90%
4. Update documentation for new test categories
5. Follow the established patterns and conventions 