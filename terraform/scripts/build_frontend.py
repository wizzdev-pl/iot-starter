"""
The utility script that builds Visualization package and moves it to .tmp directory.
It's configurable with following parameters:
FRONTEND_SOURCE_DIRECTORY (required) path to source directory of visualization
BUILD_DIR (required) path to output directory
-v, --verbose (optional) set logging level
"""
import os, pathlib, shutil, subprocess
import argparse
import logging
import typing


def parse_args():
    """
    Parse command line arguments
    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("FRONTEND_SOURCE_DIRECTORY")
    parser.add_argument("BUILD_DIR")
    parser.add_argument("-v", "--verbose", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
    return parser.parse_args()


def run_commend_in_path(path: str, command: typing.List[str]):
    """
    Temporary change current directory of python interpreter to run shell command from specified location
    :param path (str) Path to location, from where command will be run
    :param command ([str]) Command to be run
    """
    current_dir = os.getcwd()
    os.chdir(path)
    subprocess.check_call(" ".join(command), shell=True)
    os.chdir(current_dir)


def install_requirements(src_dir_path: str):
    """ Install javascript dependencies """
    logging.info("Install js dependencies")
    run_commend_in_path(src_dir_path, ["npm", "install", "--quiet"])


def build_js_package(src_dir_path: str, build_dir_path: str):
    """ Build visualization package and move it to desire directory """
    logging.info("Build js package")
    run_commend_in_path(src_dir_path, ["npm", "run", "build"])
    logging.info(f"Copy package to destination directory: {build_dir_path}")
    # Check if desire directory already exists, if so, delete it
    if os.path.isdir(build_dir_path):
        logging.debug(f"Removing old build: {build_dir_path}")
        shutil.rmtree(build_dir_path)
    js_package_path = os.path.join(src_dir_path, "dist")
    shutil.copytree(js_package_path, build_dir_path)


if __name__ == '__main__':
    # Parse arguments
    args = parse_args()
    # Set verbose levels
    logging.basicConfig(level=args.verbose)
    # Set up paths
    build_dir = pathlib.Path(args.BUILD_DIR).resolve().absolute()
    source_dir = pathlib.Path(args.FRONTEND_SOURCE_DIRECTORY).resolve().absolute()
    logging.info(f"Resolve arguments: \n BUILD_DIR: {build_dir} \n SOURCE_DIR: {source_dir}")
    # Build visualization
    install_requirements(source_dir)
    build_js_package(source_dir, build_dir)
