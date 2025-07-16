#!/usr/bin/env python3
"""
Test runner for smartmeeting.agent module tests

This script runs all agent-related tests and provides a summary of results.
"""

import sys
import os
import subprocess
from pathlib import Path


def run_agent_tests():
    """Run all agent tests and return results"""

    # Get the tests directory
    tests_dir = Path(__file__).parent
    project_root = tests_dir.parent

    # Change to project root for proper imports
    os.chdir(project_root)

    # List of test files to run
    test_files = [
        "tests/test_agent_state.py",
        "tests/test_agent_config.py",
        "tests/test_agent_tools.py",
        "tests/test_agent_nodes.py",
        "tests/test_agent_graph.py",
        "tests/test_agent_integration.py",
    ]

    print("🧪 Running smartmeeting.agent module tests...")
    print("=" * 60)

    results = {}
    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"⚠️  Test file not found: {test_file}")
            continue

        print(f"\n📋 Running tests in: {test_file}")
        print("-" * 40)

        try:
            # Run pytest on the specific test file
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout per test file
                env={**os.environ, "PYTHONPATH": str(project_root)},
            )

            # Parse results
            output_lines = result.stdout.split("\n")
            test_results = []

            for line in output_lines:
                if line.startswith("tests/") and ("::" in line):
                    if "PASSED" in line:
                        test_results.append(("PASS", line))
                        passed_tests += 1
                    elif "FAILED" in line:
                        test_results.append(("FAIL", line))
                        failed_tests += 1
                    elif "ERROR" in line:
                        test_results.append(("ERROR", line))
                        failed_tests += 1

            total_tests += len(test_results)
            results[test_file] = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "tests": test_results,
            }

            # Print test results
            for status, test_line in test_results:
                if status == "PASS":
                    print(f"✅ {test_line}")
                else:
                    print(f"❌ {test_line}")

            if result.stderr:
                print(f"⚠️  Warnings/Errors:\n{result.stderr}")

        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout running tests in {test_file}")
            results[test_file] = {"error": "timeout"}
            failed_tests += 1
        except Exception as e:
            print(f"💥 Error running tests in {test_file}: {e}")
            results[test_file] = {"error": str(e)}
            failed_tests += 1

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total test files: {len(test_files)}")
    print(f"Total tests run: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")

    if failed_tests == 0:
        print("\n🎉 All agent tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed_tests} tests failed. Check output above for details.")
        return False


def main():
    """Main function"""
    print("🚀 SmartMeeting Agent Test Suite")
    print("Testing the migrated AI meeting booking assistant")
    print()

    success = run_agent_tests()

    if success:
        print("\n✨ Agent module is ready for use!")
        sys.exit(0)
    else:
        print("\n🔧 Please fix failing tests before using the agent module.")
        sys.exit(1)


if __name__ == "__main__":
    main()
