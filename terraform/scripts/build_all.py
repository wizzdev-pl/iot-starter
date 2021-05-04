"""
The utility script that's responsible for building all software packages for cloud's part of iot-project
It runs building scripts for lambdas, REST API and Visualization
"""
import subprocess
import shutil


def _check_python():
    """Returns the path to the python 3.x.x binary"""
    py = 'python'
    py3 = 'python3'

    py_path = shutil.which(py)
    if py_path is not None:
        # Python binary 'python' exists
        py_ver = subprocess.run([py_path, '--version'], capture_output=True).stdout
        
        # Decode and get major version of python bin
        _, ver = py_ver.decode().strip().split()
        if ver.split('.')[0] == '3':
            # Binary is version 3.X.X
            return py
        else:
            # Binary is version 2.X.X - use 'python3'
            return py3


if __name__ == '__main__':
    # Get python version
    python = _check_python()

    # Run build script for REST API
    subprocess.check_call(
        [python, "build_lambda.py", "../../web_server/server", "../.tmp/rest_api",
         "--include-db-access"])

    # Run build script for lambda_collect_measurements
    subprocess.check_call(
        [python, "build_lambda.py", "../../lambda_collect_measurements", "../.tmp/lambda_collect_measurements",
         "--include-db-access"])

    # Run build script for lambda_health_check
    subprocess.check_call(
        [python, "build_lambda.py", "../../lamba_health_check", "../.tmp/lambda_health_check",
         "--include-db-access"])

    # Run build script for visualization
    subprocess.check_call(
        [python, "build_frontend.py", "../../web_server/client", "../.tmp/build_visualization"])
