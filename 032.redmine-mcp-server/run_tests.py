#!/usr/bin/env python3
"""
Test runner script with coverage reporting
"""

import subprocess
import sys
import os

def run_tests_with_coverage():
    """Run tests with coverage reporting"""
    
    # Install test dependencies if needed
    print("Installing test dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "scripts/requirements.txt"], check=True)
    
    # Run unit tests with coverage
    print("\n" + "="*60)
    print("Running Unit Tests with Coverage")
    print("="*60)
    
    coverage_cmd = [
        sys.executable, "-m", "pytest",
        "--cov=src",
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "-v",
        "-m", "not integration",
        "tests/"
    ]
    
    try:
        result = subprocess.run(coverage_cmd, check=False)
        
        if result.returncode == 0:
            print("\n✅ All unit tests passed!")
        else:
            print(f"\n❌ Some tests failed (exit code: {result.returncode})")
        
        # Show coverage report location
        htmlcov_path = os.path.abspath("htmlcov/index.html")
        if os.path.exists(htmlcov_path):
            print(f"\n📊 Coverage report generated: file://{htmlcov_path}")
        
        return result.returncode
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Test execution failed: {e}")
        return e.returncode

def run_integration_tests():
    """Run integration tests separately"""
    print("\n" + "="*60)
    print("Running Integration Tests")
    print("="*60)
    print("Note: Integration tests require a running Redmine instance and credentials")
    
    integration_cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "-m", "integration",
        "tests/"
    ]
    
    try:
        result = subprocess.run(integration_cmd, check=False)
        
        if result.returncode == 0:
            print("\n✅ All integration tests passed!")
        else:
            print(f"\n❌ Some integration tests failed or were skipped (exit code: {result.returncode})")
        
        return result.returncode
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Integration test execution failed: {e}")
        return e.returncode

def main():
    """Main test runner"""
    print("Redmine MCP Server Test Suite")
    print("="*60)
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Run unit tests with coverage
    unit_result = run_tests_with_coverage()
    
    # Ask if user wants to run integration tests
    if input("\nRun integration tests? (y/N): ").lower().startswith('y'):
        integration_result = run_integration_tests()
    else:
        integration_result = 0
        print("Skipping integration tests")
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Unit tests: {'✅ PASSED' if unit_result == 0 else '❌ FAILED'}")
    print(f"Integration tests: {'✅ PASSED' if integration_result == 0 else '❌ FAILED/SKIPPED'}")
    
    return max(unit_result, integration_result)

if __name__ == "__main__":
    sys.exit(main())