import random
import pathlib


def generate_suffix(directory: pathlib.Path = None) -> str:
    '''Generates a random suffix to avoid name conflicts.

        Optional arg: directory (str): Checks if the suffix is unique in the given directory.
    '''

    if directory:
        while True:
            suffix = random.randint(10000, 20000)
            if not list(directory.glob(str(suffix))):
                break
    else:
        suffix = random.randint(10000, 20000)
    
    return str(suffix)  