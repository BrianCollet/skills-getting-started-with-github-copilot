#!/workspaces/skills-getting-started-with-github-copilot/.venv/bin/python
"""
Test runner script for the FastAPI application
"""
import subprocess
import sys
import os

def run_tests(coverage=False, verbose=False):
    """Run the test suite with optional coverage and verbosity"""
    # Change to the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    os.chdir(script_dir)
    
    cmd = [sys.executable, '-m', 'pytest', 'tests/']
    
    if verbose:
        cmd.append('-v')
    
    if coverage:
        cmd.extend(['--cov=src', '--cov-report=term-missing'])
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run FastAPI tests")
    parser.add_argument('--coverage', '-c', action='store_true', 
                       help='Run tests with coverage report')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Run tests in verbose mode')
    
    args = parser.parse_args()
    
    exit_code = run_tests(coverage=args.coverage, verbose=args.verbose)
    sys.exit(exit_code)