from pathlib import Path


def file_exists(path: str):
    if Path(path).is_file():
        return True
    else:
        return False