import os
import json
import subprocess

TERRAFORM_DIR = "../terraform"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
TERRAFORM_BINARY_NAME = "terraform"
TERRAFORM_LOCAL_EXE = "./terraform"


def save_terraform_output_as_file(_output_file_name: str):
    # create paths to terraform directory
    terraform_full_path = os.path.join(ROOT_DIR, TERRAFORM_DIR)

    # change current working directory
    # it is necessary because terraform is initialized in cwd
    old_cwd = os.getcwd()
    os.chdir(terraform_full_path)

    # get terraform output
    tf_output_str = create_terraform_output()

    # come back to old working directory
    os.chdir(old_cwd)

    # save output to file
    print("Saving terraform output to file...")
    with open(_output_file_name, 'w') as outfile:
        outfile.write(tf_output_str)


def create_terraform_output() -> str:
    subprocess.run([TERRAFORM_LOCAL_EXE, "init"])
    subprocess.run([TERRAFORM_LOCAL_EXE, "workspace", "select", "production"])
    proc = subprocess.Popen([TERRAFORM_LOCAL_EXE, 'output', '-json'], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    return get_string_from_byte(output)


def get_string_from_byte(_output: bytes) -> str:
    output_json = _output.decode('utf-8')
    output_dict = json.loads(output_json)
    output_str = json.dumps(output_dict, indent=4, sort_keys=True)
    return output_str
