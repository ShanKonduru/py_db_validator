#!/usr/bin/env python
"""
PostgreSQL Smoke Tests - Environment Variable Example
Demonstrates how to run PostgreSQL smoke tests using environment variables
"""
import os
import subprocess
import sys


def test_with_environment_variables():
    """Example of running PostgreSQL smoke tests with environment variables"""

    print("=" * 60)
    print("PostgreSQL Smoke Tests - Environment Variable Example")
    print("=" * 60)

    # Example configuration - replace with your actual values
    test_config = {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_DATABASE": "postgres",
        "POSTGRES_USERNAME": "postgres",
        "POSTGRES_PASSWORD": "password",
        "POSTGRES_SCHEMA": "public",
    }

    print("Setting up test environment variables:")
    for key, value in test_config.items():
        if key == "POSTGRES_PASSWORD":
            print(f"  {key}: {'*' * len(value)}")
        else:
            print(f"  {key}: {value}")
        os.environ[key] = value

    print("\nRunning PostgreSQL smoke tests...")
    print("-" * 60)

    try:
        # Run the smoke tests
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_postgresql_smoke.py", "-v"],
            check=True,
            capture_output=True,
            text=True,
        )

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print("=" * 60)
        print("✅ SUCCESS: PostgreSQL smoke tests passed with environment variables!")
        print("=" * 60)

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: Tests failed with return code {e.returncode}")
        print("\nSTDOUT:")
        print(e.stdout)
        print("\nSTDERR:")
        print(e.stderr)
        print("=" * 60)

        return False

    finally:
        # Clean up environment variables
        print("\nCleaning up environment variables...")
        for key in test_config.keys():
            if key in os.environ:
                del os.environ[key]


def test_with_different_environment():
    """Example of testing with different environment/application"""

    print("=" * 60)
    print("Testing Different Environment/Application Configuration")
    print("=" * 60)

    # Set test environment and application
    os.environ["TEST_ENVIRONMENT"] = "PROD"
    os.environ["TEST_APPLICATION"] = "MYAPP"

    try:
        # This should fail because PROD/MYAPP doesn't exist in our config
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/test_postgresql_smoke.py::TestPostgreSQLSmoke::test_environment_setup",
                "-v",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(
                "✅ EXPECTED: Test correctly failed for non-existent PROD/MYAPP configuration"
            )
            print(
                "This demonstrates the flexible configuration system working correctly."
            )
        else:
            print(
                "❌ UNEXPECTED: Test should have failed for non-existent configuration"
            )

    finally:
        # Clean up
        if "TEST_ENVIRONMENT" in os.environ:
            del os.environ["TEST_ENVIRONMENT"]
        if "TEST_APPLICATION" in os.environ:
            del os.environ["TEST_APPLICATION"]


def main():
    """Main demonstration function"""
    print("PostgreSQL Smoke Tests - Configuration Examples\n")

    # Example 1: Environment variables (if you want to test with real DB)
    print("Example 1: Environment Variable Configuration")
    print("NOTE: This example uses dummy values. Update test_config in the code")
    print("      with your actual PostgreSQL connection details to test.\n")

    # Example 2: Different environment/application
    print("Example 2: Testing Configuration Validation")
    test_with_different_environment()

    print("\n" + "=" * 60)
    print("Configuration Examples Complete!")
    print("=" * 60)
    print("\nTo run actual tests with your PostgreSQL database:")
    print("1. Update the test_config dictionary with your connection details")
    print("2. Uncomment the test_with_environment_variables() call below")
    print("3. Run this script")
    print("\nAlternatively, set environment variables manually and run:")
    print("   pytest tests/test_postgresql_smoke.py -v")


if __name__ == "__main__":
    main()

    # Uncomment the line below to test with actual environment variables
    # test_with_environment_variables()
