from pathlib import Path


def file_exists(path: str) -> bool:
    if Path(path).is_file():
        return True
    else:
        return False


def remove_file(path: str, suppress=False) -> None:
    if file_exists(path):
        Path(path).unlink()
    else:
        if not suppress:
            print("File under path: {} does not exist!".format(path))
