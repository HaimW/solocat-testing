# Quick Start Guide - Linux

## 🚀 One-Command Setup

```bash
# Clone repository
git clone <your-repository>
cd audio-processing-system

# Setup and run tests
make setup && make test
```

## 📋 Step-by-Step Setup

### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-venv
sudo apt-get install libpq-dev postgresql-client build-essential
```

**CentOS/RHEL/Rocky:**
```bash
sudo dnf install python3-devel python3-pip
sudo dnf install postgresql-devel gcc gcc-c++ make
```

### 2. Setup Project
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run setup script
./scripts/setup.sh
```

### 3. Run Tests
```bash
# Demo tests (quick verification)
./scripts/run_tests.sh demo

# All tests with parallel execution
./scripts/run_tests.sh all --parallel

# Generate coverage report
./scripts/run_tests.sh coverage
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
| `make test` | Run demo tests |
| `make test-all` | Run complete test suite |
| `make coverage` | Generate coverage report |
| `make docker-up` | Start Docker environment |
| `make clean` | Clean temporary files |
| `make help` | Show all available commands |

## ✅ Quick Verification

After setup, verify everything works:

```bash
# Check system
make check

# Run basic tests
python pytest/demo_test.py

# View test results
ls -la test-reports/
```

## 🔧 Troubleshooting

**Permission denied on scripts:**
```bash
chmod +x scripts/*.sh
```

**Missing Python packages:**
```bash
pip install -r pytest/requirements-minimal.txt
```

**PostgreSQL connection issues:**
```bash
# Use minimal setup (no database required)
./scripts/run_tests.sh demo
```

---

**Ready to test!** All tests should pass on a fresh Linux system. 