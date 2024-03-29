import argparse
import os
import sys
from pathlib import Path

import git
from git.refs.tag import TagReference

import pyboard

ROOT_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))
MICROPYTHON_FILESYSTEM_SEPARATOR = "/"

esp_board = None

DEVICE_RESOURCES_FILE_DIR = "/resources"

def remove_some_dirs_from_path():
    # because there may be a library that interferes with ampy (and actually is)
    dirs_to_remove = ['lib', 'stabs']
    python_path = os.environ.get('PYTHONPATH', '').split(':')

    for dir_to_remove in dirs_to_remove:
        full_path = os.path.join(ROOT_DIR, dir_to_remove)
        try:
            sys.path.remove(full_path)
            python_path.remove(full_path)
        except:
            pass
    os.environ['PYTHONPATH'] = ':'.join(python_path)


CACHE = {
    'dirs': [],
    'files': {
        'eXaMpLe': 2312312331  # upload timestamp
    }
}


def is_ignored_file(file: str, cloud: str, config_name: str):
    if file.endswith('.orig'):
        return True
    if file.endswith('.pyc'):
        return True
    if file.endswith('.json') and cloud.lower() not in file.lower() and file != config_name:
        return True
    if file in ['__pycache__']:
        return True
    return False


def _create_dir(path):
    if path in CACHE['dirs']:
        print(f'Directory "{path}" already in Cache')
        return

    print(f'Creating directory "{path}"')
    try:
        esp_board.fs_mkdir(path)
    except pyboard.PyboardError as e:
        if 'exist' in str(e).lower():
            pass
        else:
            print(str(e))
            raise Exception('Failed to create dir!')
    CACHE['dirs'].append(path)


def upload_file(full_repo_file_path, dev_file_path):
    modification_time = float(os.path.getmtime(full_repo_file_path))
    if CACHE['files'].get(dev_file_path, 0) >= modification_time:
        print(
            f'File "{dev_file_path}" already in Cache after modification time')
        return

    print(f'# Uploading file "{dev_file_path}"')
    try:
        op = esp_board.fs_put
        print("cp %s : %s" % (full_repo_file_path, dev_file_path))
        op(full_repo_file_path, dev_file_path)
    except pyboard.PyboardError as e:
        print(str(e))
        raise Exception('Failed to upload file!')
    else:
        CACHE['files'][dev_file_path] = modification_time


def dev_create_dir(path: str, skip_subpaths=True):
    if not path or path == "/":
        return

    parent_dir = os.path.dirname(path)
    if parent_dir and not skip_subpaths:
        dev_create_dir(path=parent_dir, skip_subpaths=False)

    _create_dir(path=path)


def upload_dir(repo_path: str, device_path, cloud: str, config_name: str):
    if device_path:
        dev_create_dir(path=device_path, skip_subpaths=False)
    full_repo_path = os.path.join(ROOT_DIR, repo_path)

    for file_name in os.listdir(full_repo_path):
        if is_ignored_file(file_name, cloud, config_name):
            continue
        
        if 'cloud' in device_path:
            if cloud.lower() not in file_name.lower() and 'interface' not in file_name:
                continue
        
        if cloud.lower() != 'blynk':
            if file_name == 'BlynkLib.py':
                continue

        full_repo_file_path = os.path.join(full_repo_path, file_name)
        if os.path.isfile(full_repo_file_path):
            if device_path:
                dev_file_path = device_path + MICROPYTHON_FILESYSTEM_SEPARATOR + file_name
            else:
                dev_file_path = file_name
            try:
                upload_file(full_repo_file_path=full_repo_file_path,
                            dev_file_path=dev_file_path)
            except:
                print('!!!!!!!RETRYING!!!!')
                upload_file(full_repo_file_path=full_repo_file_path,
                            dev_file_path=dev_file_path)

        else:
            devive_directory_name = device_path + \
                MICROPYTHON_FILESYSTEM_SEPARATOR + file_name

            upload_dir(repo_path=full_repo_file_path,
                       device_path=devive_directory_name, cloud=cloud, config_name=config_name)


def _read_commit_info():
    repo = git.Repo(search_parent_directories=True)

    if repo is not None:
        # last tag on the list is the newest one
        tagref = TagReference.list_items(repo)[-1]

        hash_last_commit = repo.head.object.hexsha

        if tagref is not None:
            hash_last_tag = tagref.tag.object.hexsha

            if hash_last_commit == hash_last_tag:
                tag = tagref.tag.tag
                return hash_last_commit, tag  # return hash and tag of last commit if it was tagged
            else:
                return hash_last_commit, "None"  # return only hash of last commit otherwise
        else:
            # return hash of last commit if there's no tags in repository
            return hash_last_commit, "No tagged commits"

    else:
        print("Repository info not found")
        return "Unknown", "Unknown"


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', metavar='PORT', type=str, required=True,
                        help="Com port of the device")
    parser.add_argument('--config-path', metavar='CONFIG', type=str, required=True,
                        help="Set credentials needed for cloud service")
    parser.add_argument('-f', '--force', action='store_true',
                        help='Upload all files again, even if not modified since caching')

    args = vars(parser.parse_args())
    return args


def flash_scripts(port, cloud_config_file_path, cloud, config_name):
    global esp_board

    remove_some_dirs_from_path()

    esp_board = pyboard.Pyboard(port, 115200)
    try:
        esp_board.enter_raw_repl()
    except pyboard.PyboardError as er:
        print(er)
        esp_board.close()
        sys.exit(1)

    upload_dir(repo_path='src', device_path='', cloud=cloud, config_name=config_name)
    dev_create_dir(DEVICE_RESOURCES_FILE_DIR)

    cloud_config_device_path = DEVICE_RESOURCES_FILE_DIR + \
        "/" + Path(cloud_config_file_path).name
    cloud_config_file_path = os.path.abspath(cloud_config_file_path)
    upload_file(cloud_config_file_path, cloud_config_device_path)

    print('Finished!')


if __name__ == '__main__':
    args = parse_arguments()

    flash_scripts(args['port'], args['config_path'])
