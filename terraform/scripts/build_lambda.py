"""
The utility script that builds lambda package and moves it to .tmp directory.
It's configurable with following parameters:
LAMBDA_SOURCE_DIRECTORY (required) path to source directory of lambda
BUILD_DIR (required) path to output directory
--include-db-access (flag) include db_access library in output directory
-v, --verbose (optional) set logging level
"""
import os, pathlib, shutil, subprocess
import argparse
import logging

# Set up path to db access library
# This is a package that standardize using of database in iot-project
DB_ACCESS_LIBRARY_PATH = pathlib.Path(os.path.dirname(__file__), '..', '..', 'db_access').absolute()


def parse_args():
    """
    Parse command line arguments
    :return argparse.Namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("LAMBDA_SOURCE_DIRECTORY")
    parser.add_argument("BUILD_DIR")
    parser.add_argument("--include-db-access", action="store_true", default=False, dest="add_db_access")
    parser.add_argument("-v", "--verbose", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
    return parser.parse_args()


def clean_src_dir(src_dir_path: str):
    """
    Remove cache directories from python source directory.
    It searches for __pycache__ dirs and remove them with whole content
    :param src_dir_path: (str) path to source directory
    """
    logging.debug(f"Clean dir: {src_dir_path}")
    for entry in os.scandir(src_dir_path):
        if entry.name == "__pycache__":
            shutil.rmtree(entry.path)
        elif entry.is_dir():
            clean_src_dir(entry.path)


def clean_build_dir(build_dir_path: str):
    """
    Check if output directory already exists, if so clean it's contents.
    :param build_dir_path: (str) path to build directory
    """
    logging.info(f"Clean build dir: {build_dir_path}")
    if os.path.isdir(build_dir_path):
        logging.debug(f"Remove {build_dir_path}")
        shutil.rmtree(build_dir_path, ignore_errors=True)
    logging.debug(f"Create empty directory: {build_dir_path}")
    pathlib.Path(build_dir_path).mkdir(parents=True, exist_ok=True)


def install_requirements(src_dir_path: str, build_dir_path: str, add_db_access: bool = False):
    """
    Find files with python dependencies and install them into output directory.
    :param src_dir_path: (str) path to source directory of lambda
    :param build_dir_path: (str) path to output directory
    :param add_db_access: (bool) flag, if db_access library has to be included in output
    """
    logging.debug("Install dependencies")
    src_requirements_txt_path = os.path.join(str(src_dir_path), "requirements.txt")
    db_access_requirements_txt_path = os.path.join(DB_ACCESS_LIBRARY_PATH, "requirements.txt")
    # Install lambda dependencies
    if os.path.isfile(src_requirements_txt_path):
        subprocess.check_call(["pip", "install", "-r", str(src_requirements_txt_path), "--target", str(build_dir_path), "-qqq"])
    # Install db_access dependencies and copy db_access package to output directory
    if add_db_access:
        logging.debug("Add DB-ACCESS to packages")
        if os.path.isfile(db_access_requirements_txt_path):
            subprocess.check_call(["pip", "install", "-r", str(db_access_requirements_txt_path), "--target", str(build_dir_path), "-qqq"])
        db_access_dir_name = os.path.basename(DB_ACCESS_LIBRARY_PATH)
        shutil.copytree(DB_ACCESS_LIBRARY_PATH, os.path.join(build_dir_path, db_access_dir_name))
        for entry in os.scandir(DB_ACCESS_LIBRARY_PATH):
            if entry.is_dir():
                shutil.copytree(entry.path, os.path.join(build_dir_path, entry.name))
            elif entry.is_file():
                shutil.copy2(entry.path, os.path.join(build_dir_path, entry.name))


def copy_lambda_code(src_dir_path: str, build_dir_path: str):
    """
    Copy code of lambda to output directory
    :param src_dir_path: (str) directory with source code
    :param build_dir_path: (str) path to output directory
    """
    logging.info("Copy lambda code")
    for entry in os.scandir(src_dir_path):
        if entry.is_dir():
            shutil.copytree(entry.path, os.path.join(build_dir_path, entry.name))
        elif entry.is_file():
            shutil.copy2(entry.path, os.path.join(build_dir_path, entry.name))


if __name__ == '__main__':
    # Parse arguments
    args = parse_args()
    # Set verbose levels
    logging.basicConfig(level=args.verbose)
    # Set up paths
    build_dir = pathlib.Path(args.BUILD_DIR).resolve()
    lambda_source_dir = pathlib.Path(args.LAMBDA_SOURCE_DIRECTORY).resolve()
    logging.info(f"Resolve arguments: "
                 f"\n BUILD_DIR: {build_dir} "
                 f"\n SOURCE_DIR: {lambda_source_dir} "
                 f"\n Add DB-ACCESS: {args.add_db_access}")
    # Build lambda
    clean_src_dir(DB_ACCESS_LIBRARY_PATH)
    clean_src_dir(lambda_source_dir)
    clean_build_dir(build_dir)
    install_requirements(lambda_source_dir, build_dir, args.add_db_access)
    copy_lambda_code(lambda_source_dir, build_dir)
