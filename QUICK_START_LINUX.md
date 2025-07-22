# Quick Start Guide

## 🚀 One-Command Setup

```bash
# Clone and setup
git clone <your-repository>
cd solocat-testing
make setup && make test
```

## 📋 Step-by-Step Setup

### 1. Basic Setup
```bash
# Make scripts executable and setup
chmod +x scripts/*.sh
./scripts/setup.sh
```

### 2. Run Tests
```bash
# Quick validation (recommended)
make test

# Demo tests for verification
./scripts/run_tests.sh demo

# Full test suite
make test-all
```

## 🐳 Docker Alternative

```bash
# Build and run in Docker
docker build -t audio-processing-tests .
docker run audio-processing-tests

# Full environment with services
docker-compose up -d
```

## 📊 Available Commands

| Command | Description |
|---------|-------------|
| `make test` | Run validation tests |
| `make test-all` | Run complete test suite |
| `make coverage` | Generate coverage report |
| `make docker-up` | Start Docker environment |
| `make clean` | Clean temporary files |
| `make help` | Show all available commands |

## ✅ Quick Verification

```bash
# Check system
make check

# Run basic tests  
python pytest/demo_test.py

# Check results
echo "Setup complete!"
```

## 🔧 Troubleshooting

**Permission issues:**
```bash
chmod +x scripts/*.sh
```

**Python packages:**
```bash
pip install -r pytest/requirements.txt
```

**Quick test:**
```bash
./scripts/run_tests.sh demo
```

---

**Ready to test!** The framework is now set up with comprehensive mocking. 