"""
The utility script that's responsible for building all software packages for cloud's part of iot-project
It runs building scripts for lambdas, REST API and Visualization
"""
import subprocess

if __name__ == '__main__':
    # Run build script for REST API
    subprocess.check_call(
        ["python3", "build_lambda.py", "../../web_server/server", "../.tmp/rest_api",
         "--include-db-access"])

    # Run build script for lambda_collect_measurements
    subprocess.check_call(
        ["python3", "build_lambda.py", "../../lambda_collect_measurements", "../.tmp/lambda_collect_measurements",
         "--include-db-access"])

    # Run build script for lambda_health_check
    subprocess.check_call(
        ["python3", "build_lambda.py", "../../lamba_health_check", "../.tmp/lambda_health_check",
         "--include-db-access"])

    # Run build script for visualization
    subprocess.check_call(
        ["python3", "build_frontend.py", "../../web_server/client", "../.tmp/build_visualization"])
