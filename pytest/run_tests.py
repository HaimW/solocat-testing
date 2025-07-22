#!/usr/bin/env python3
"""
Audio Processing System Test Runner

A comprehensive test runner script that provides different execution modes
and reporting options for the Audio Processing System test suite.
"""

import argparse
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional


class TestRunner:
    """Test runner with various execution modes and reporting capabilities."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.coverage_threshold = 90
        self.performance_thresholds = {
            "algorithm_a_avg_time": 0.2,
            "algorithm_b_avg_time": 0.15,
            "message_broker_throughput": 500,
            "database_write_latency": 0.01,
            "api_response_time": 0.5
        }
    
    def run_unit_tests(self, verbose: bool = False, coverage: bool = True) -> int:
        """Run unit tests with optional coverage reporting."""
        print("🧪 Running Unit Tests...")
        
        cmd = ["pytest", "-m", "unit"]
        
        if verbose:
            cmd.append("-v")
        
        if coverage:
            cmd.extend([
                "--cov=audio_processing",
                "--cov=message_broker", 
                "--cov=database",
                "--cov=api",
                f"--cov-fail-under={self.coverage_threshold}",
                "--cov-report=term-missing",
                "--cov-report=html:coverage_html/unit"
            ])
        
        return self._execute_command(cmd)
    
    def run_functional_tests(self, verbose: bool = False) -> int:
        """Run functional and integration tests."""
        print("🔄 Running Functional Tests...")
        
        cmd = ["pytest", "-m", "functional"]
        
        if verbose:
            cmd.append("-v")
        
        cmd.extend([
            "--tb=short",
            "--durations=10",
            "--junit-xml=test_results_functional.xml"
        ])
        
        return self._execute_command(cmd)
    
    def run_performance_tests(self, save_baseline: bool = False, compare_baseline: bool = False) -> int:
        """Run performance and load tests."""
        print("⚡ Running Performance Tests...")
        
        cmd = ["pytest", "-m", "performance", "--tb=short"]
        
        if save_baseline:
            cmd.append("--benchmark-save=baseline")
            print("📊 Saving performance baseline...")
        
        if compare_baseline:
            cmd.append("--benchmark-compare=baseline")
            print("📈 Comparing against baseline...")
        
        cmd.extend([
            "--junit-xml=test_results_performance.xml",
            "--benchmark-json=performance_results.json"
        ])
        
        return self._execute_command(cmd)
    
    def run_security_tests(self, verbose: bool = False) -> int:
        """Run security and vulnerability tests."""
        print("🔒 Running Security Tests...")
        
        cmd = ["pytest", "-m", "security"]
        
        if verbose:
            cmd.extend(["-v", "--tb=long"])
        else:
            cmd.append("--tb=short")
        
        cmd.extend([
            "--junit-xml=test_results_security.xml",
            "--json-report",
            "--json-report-file=security_report.json"
        ])
        
        return self._execute_command(cmd)
    
    def run_all_tests(self, skip_slow: bool = False, parallel: bool = False) -> int:
        """Run all test suites."""
        print("🚀 Running Complete Test Suite...")
        
        cmd = ["pytest"]
        
        if skip_slow:
            cmd.extend(["-m", "not slow"])
            print("⏩ Skipping slow tests...")
        
        if parallel:
            cmd.extend(["-n", "auto"])
            print("🔀 Running tests in parallel...")
        
        cmd.extend([
            "--cov=.",
            f"--cov-fail-under={self.coverage_threshold}",
            "--cov-report=html:coverage_html/all",
            "--cov-report=xml:coverage.xml",
            "--junit-xml=test_results_all.xml",
            "--tb=short",
            "--durations=20"
        ])
        
        return self._execute_command(cmd)
    
    def run_smoke_tests(self) -> int:
        """Run a quick smoke test suite for CI/CD pipelines."""
        print("💨 Running Smoke Tests...")
        
        cmd = [
            "pytest",
            "-m", "unit and not slow",
            "--maxfail=5",
            "--tb=short",
            "--quiet"
        ]
        
        return self._execute_command(cmd)
    
    def run_regression_tests(self) -> int:
        """Run regression tests to ensure no functionality is broken."""
        print("🔄 Running Regression Tests...")
        
        cmd = [
            "pytest",
            "-m", "functional or integration",
            "--tb=short",
            "--strict-markers",
            "--junit-xml=test_results_regression.xml"
        ]
        
        return self._execute_command(cmd)
    
    def run_load_tests(self, duration: int = 60) -> int:
        """Run extended load tests."""
        print(f"🏋️ Running Load Tests (Duration: {duration}s)...")
        
        # Set environment variable for test duration
        env = os.environ.copy()
        env["LOAD_TEST_DURATION"] = str(duration)
        
        cmd = [
            "pytest",
            "-m", "performance and slow",
            "--tb=short",
            "--junit-xml=test_results_load.xml"
        ]
        
        return self._execute_command(cmd, env=env)
    
    def generate_test_report(self) -> None:
        """Generate comprehensive test report."""
        print("📋 Generating Test Report...")
        
        report_dir = self.base_dir / "test_reports"
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"test_report_{int(time.time())}.html"
        
        # Generate HTML report combining all test results
        cmd = [
            "pytest-html-merger",
            "--input", "test_results_*.xml",
            "--output", str(report_file)
        ]
        
        try:
            self._execute_command(cmd)
            print(f"📄 Test report generated: {report_file}")
        except subprocess.CalledProcessError:
            print("⚠️ Could not generate HTML report (pytest-html-merger not available)")
    
    def check_test_environment(self) -> bool:
        """Check if test environment is properly configured."""
        print("🔍 Checking Test Environment...")
        
        # Check required dependencies
        required_packages = [
            "pytest", "pytest-asyncio", "pytest-cov", 
            "pytest-mock", "pytest-timeout"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            print("💡 Run: pip install -r requirements.txt")
            return False
        
        # Check test configuration
        pytest_ini = self.base_dir / "pytest.ini"
        if not pytest_ini.exists():
            print("❌ pytest.ini configuration file not found")
            return False
        
        print("✅ Test environment is properly configured")
        return True
    
    def clean_test_artifacts(self) -> None:
        """Clean up test artifacts and temporary files."""
        print("🧹 Cleaning Test Artifacts...")
        
        artifacts_to_clean = [
            ".pytest_cache",
            "__pycache__",
            "*.pyc",
            ".coverage",
            "coverage_html",
            "test_results_*.xml",
            "performance_results.json",
            "security_report.json",
            ".benchmarks"
        ]
        
        for pattern in artifacts_to_clean:
            cmd = ["find", ".", "-name", pattern, "-delete"]
            try:
                subprocess.run(cmd, check=False, capture_output=True)
            except subprocess.CalledProcessError:
                pass
        
        print("✅ Test artifacts cleaned")
    
    def _execute_command(self, cmd: List[str], env: Optional[Dict[str, str]] = None) -> int:
        """Execute a command and return the exit code."""
        print(f"🔧 Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.base_dir,
                env=env or os.environ,
                check=False
            )
            
            if result.returncode == 0:
                print("✅ Command completed successfully")
            else:
                print(f"❌ Command failed with exit code {result.returncode}")
            
            return result.returncode
        
        except KeyboardInterrupt:
            print("\n⏹️ Test execution interrupted by user")
            return 130
        except Exception as e:
            print(f"💥 Error executing command: {e}")
            return 1


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Audio Processing System Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s unit --verbose --coverage        # Run unit tests with coverage
  %(prog)s functional                       # Run functional tests
  %(prog)s performance --save-baseline      # Run and save performance baseline
  %(prog)s security --verbose               # Run security tests with detailed output
  %(prog)s all --parallel --skip-slow       # Run all tests in parallel, skip slow ones
  %(prog)s smoke                            # Quick smoke test for CI/CD
  %(prog)s load --duration 300              # Run load tests for 5 minutes
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Test execution mode")
    
    # Unit tests
    unit_parser = subparsers.add_parser("unit", help="Run unit tests")
    unit_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    unit_parser.add_argument("--no-coverage", action="store_true", help="Skip coverage reporting")
    
    # Functional tests
    functional_parser = subparsers.add_parser("functional", help="Run functional tests")
    functional_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # Performance tests
    performance_parser = subparsers.add_parser("performance", help="Run performance tests")
    performance_parser.add_argument("--save-baseline", action="store_true", help="Save performance baseline")
    performance_parser.add_argument("--compare-baseline", action="store_true", help="Compare against baseline")
    
    # Security tests
    security_parser = subparsers.add_parser("security", help="Run security tests")
    security_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # All tests
    all_parser = subparsers.add_parser("all", help="Run all tests")
    all_parser.add_argument("--skip-slow", action="store_true", help="Skip slow tests")
    all_parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    
    # Smoke tests
    subparsers.add_parser("smoke", help="Run quick smoke tests")
    
    # Regression tests
    subparsers.add_parser("regression", help="Run regression tests")
    
    # Load tests
    load_parser = subparsers.add_parser("load", help="Run load tests")
    load_parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    
    # Utility commands
    subparsers.add_parser("check", help="Check test environment")
    subparsers.add_parser("clean", help="Clean test artifacts")
    subparsers.add_parser("report", help="Generate test report")
    
    # Global options
    parser.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    runner = TestRunner()
    
    # Check environment before running tests
    if args.command in ["unit", "functional", "performance", "security", "all", "smoke", "regression", "load"]:
        if not runner.check_test_environment():
            return 1
    
    # Execute the requested command
    exit_code = 0
    
    try:
        if args.command == "unit":
            exit_code = runner.run_unit_tests(
                verbose=args.verbose,
                coverage=not args.no_coverage
            )
        
        elif args.command == "functional":
            exit_code = runner.run_functional_tests(verbose=args.verbose)
        
        elif args.command == "performance":
            exit_code = runner.run_performance_tests(
                save_baseline=args.save_baseline,
                compare_baseline=args.compare_baseline
            )
        
        elif args.command == "security":
            exit_code = runner.run_security_tests(verbose=args.verbose)
        
        elif args.command == "all":
            exit_code = runner.run_all_tests(
                skip_slow=args.skip_slow,
                parallel=args.parallel
            )
        
        elif args.command == "smoke":
            exit_code = runner.run_smoke_tests()
        
        elif args.command == "regression":
            exit_code = runner.run_regression_tests()
        
        elif args.command == "load":
            exit_code = runner.run_load_tests(duration=args.duration)
        
        elif args.command == "check":
            success = runner.check_test_environment()
            exit_code = 0 if success else 1
        
        elif args.command == "clean":
            runner.clean_test_artifacts()
            exit_code = 0
        
        elif args.command == "report":
            runner.generate_test_report()
            exit_code = 0
        
        # Summary
        if exit_code == 0 and args.command in ["unit", "functional", "performance", "security", "all"]:
            print("\n🎉 All tests passed successfully!")
        elif exit_code != 0:
            print(f"\n💥 Tests failed with exit code {exit_code}")
    
    except KeyboardInterrupt:
        print("\n⏹️ Test execution interrupted")
        exit_code = 130
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main()) 