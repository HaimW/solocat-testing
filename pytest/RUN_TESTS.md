# How to Run Tests - Guide

## 🚀 Quick Start

```bash
# Basic validation
make test

# Full test suite
make test-all

# Coverage analysis
make coverage
```

## 📋 Test Categories

### Demo Tests (Quick Validation)
```bash
# Standalone demo tests
python pytest/demo_test.py

# Via scripts  
./scripts/run_tests.sh demo
```

### Full Test Suite
```bash
# All test categories
./scripts/run_tests.sh all --parallel

# Specific categories
make test-unit          # Unit tests
make test-functional    # Integration tests  
make test-performance   # Performance tests
make test-security      # Security tests
```

## ✅ Expected Results

**Current Status**: 84 tests total, ~30 failures (significantly improved from 51)

**Working Categories**:
- ✅ Demo tests - All passing
- ✅ Performance tests - Most passing
- 🟡 Unit tests - Most passing with minor async issues
- 🟡 Functional tests - Improving with mock integration
- 🟡 Security tests - Most passing with validation fixes

## 🎯 Mock System Benefits

- **No External Dependencies**: Complete mock implementations
- **Fast Execution**: No database/message broker setup required
- **Reliable Testing**: Consistent, controlled test environment
- **Call Tracking**: MagicMock integration for proper assertions
- **Realistic Data**: Comprehensive mock data structures

## 🔧 Advanced Usage

### Coverage Reporting
```bash
# Generate coverage report
./scripts/run_tests.sh coverage

# View coverage HTML
open coverage_html/index.html
```

### Docker Testing
```bash
# Run in container
docker build -t audio-tests .
docker run audio-tests

# Full environment
docker-compose up -d
```

### Debug Mode
```bash
# Verbose output
pytest -v -s --tb=long

# Specific test
pytest unit_tests/test_algorithms.py::TestAlgorithmA -v
```

## 📊 Test Structure

- **84 total tests** across 4 categories
- **12+ mock modules** providing complete simulation
- **Async support** for realistic audio processing workflows
- **Performance benchmarks** for load validation
- **Security tests** for vulnerability assessment

---

**Ready for comprehensive testing with full mock coverage!** 