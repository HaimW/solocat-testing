# How to Run Tests - Simple Guide

## 🚀 Quick Start (Cross-Platform)

### Linux/Unix (Recommended)
```bash
# Setup (one time)
./scripts/setup.sh

# Run demo tests
./scripts/run_tests.sh demo

# Run with coverage
./scripts/run_tests.sh coverage --parallel
```

### Windows
```cmd
REM Setup (one time)
scripts\setup.bat

REM Run demo tests
scripts\run_tests.bat demo

REM Run with coverage
scripts\run_tests.bat coverage -n auto
```

### Manual Method (Any OS)
```bash
# Linux/Unix
source .venv/bin/activate
python pytest/demo_test.py

# Windows
.venv\Scripts\activate
python pytest/demo_test.py
```

## ✅ Expected Output
When successful, you should see:
```
✅ test_basic_functionality PASSED
✅ test_json_operations PASSED  
✅ test_mock_functionality PASSED
✅ test_async_functionality PASSED
✅ test_audio_data_validation PASSED
✅ test_feature_extraction_simulation PASSED
✅ test_message_processing_simulation PASSED
```

## 🔧 If You Want Full Dependencies

### For Complete Testing (Optional)
```bash
# Install full requirements (may have dependency issues)
pip install -r pytest/requirements.txt

# Run all tests
python pytest/run_tests.py unit
```

**Note:** Full requirements include PostgreSQL, Redis, and RabbitMQ dependencies that may require additional system setup on Windows.

## 🎯 Purpose

The **demo tests are sufficient** to demonstrate:
- ✅ pytest framework working
- ✅ Mocking capabilities
- ✅ Async testing
- ✅ JSON processing
- ✅ Audio processing simulation

The full test suite is designed as a **portfolio demonstration** - the mock tests show the testing strategy without requiring actual database/message broker setup.

## 📋 Available Test Files

- `demo_test.py` - Simple standalone tests ✅
- `unit_tests/` - Full unit test suite (requires dependencies)
- `functional_tests/` - Integration tests (requires dependencies)  
- `performance_tests/` - Load testing (requires dependencies)
- `security_tests/` - Security validation (requires dependencies)

Start with `demo_test.py` - it proves the concept works! 