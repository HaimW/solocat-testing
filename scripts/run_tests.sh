#!/bin/bash
# Audio Processing System - Linux/Unix Test Runner

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if virtual environment is activated
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "Virtual environment not activated"
        print_status "Activating virtual environment..."
        source "$PROJECT_ROOT/.venv/bin/activate"
    fi
}

# Function to show help
show_help() {
    echo "Audio Processing System Test Runner (Linux/Unix)"
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  demo        Run demo tests (no dependencies)"
    echo "  unit        Run unit tests"
    echo "  functional  Run functional tests"
    echo "  performance Run performance tests"
    echo "  security    Run security tests"
    echo "  all         Run all tests"
    echo "  coverage    Run tests with coverage report"
    echo "  help        Show this help"
    echo ""
    echo "Options:"
    echo "  --verbose   Verbose output"
    echo "  --quiet     Quiet output"
    echo "  --parallel  Run tests in parallel"
    echo ""
    echo "Examples:"
    echo "  $0 demo"
    echo "  $0 unit --verbose"
    echo "  $0 coverage --parallel"
}

# Main function
main() {
    local command="${1:-help}"
    local verbose=""
    local quiet=""
    local parallel=""
    
    # Parse options
    shift || true
    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose)
                verbose="-v"
                shift
                ;;
            --quiet)
                quiet="-q"
                shift
                ;;
            --parallel)
                parallel="-n auto"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    cd "$PROJECT_ROOT"
    
    case $command in
        demo)
            print_status "Running demo tests..."
            check_venv
            python pytest/demo_test.py
            ;;
        unit)
            print_status "Running unit tests..."
            check_venv
            python -m pytest pytest/unit_tests/ $verbose $quiet $parallel \
                --tb=short \
                -p no:postgresql \
                -p no:kubernetes
            ;;
        functional)
            print_status "Running functional tests..."
            check_venv
            python -m pytest pytest/functional_tests/ $verbose $quiet $parallel \
                --tb=short \
                -p no:postgresql \
                -p no:kubernetes
            ;;
        performance)
            print_status "Running performance tests..."
            check_venv
            python -m pytest pytest/performance_tests/ $verbose $quiet \
                --tb=short \
                -p no:postgresql \
                -p no:kubernetes \
                -m "not slow"
            ;;
        security)
            print_status "Running security tests..."
            check_venv
            python -m pytest pytest/security_tests/ $verbose $quiet $parallel \
                --tb=short \
                -p no:postgresql \
                -p no:kubernetes
            ;;
        all)
            print_status "Running all tests..."
            check_venv
            python -m pytest pytest/ $verbose $quiet $parallel \
                --tb=short \
                -p no:postgresql \
                -p no:kubernetes \
                --ignore=pytest/demo_test.py
            ;;
        coverage)
            print_status "Running tests with coverage..."
            check_venv
            python -m pytest pytest/ $verbose $quiet $parallel \
                --tb=short \
                -p no:postgresql \
                -p no:kubernetes \
                --ignore=pytest/demo_test.py \
                --cov=pytest \
                --cov-report=html:coverage_html \
                --cov-report=term-missing
            print_status "Coverage report generated in coverage_html/"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@" 