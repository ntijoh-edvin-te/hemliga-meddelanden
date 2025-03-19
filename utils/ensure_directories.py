import os
import pathlib

def ensure_directories():
    """Create directories for the application if they don't exist."""
    dirs = [
        "data/input",
        "data/output"
    ]
    
    for directory in dirs:
        path = pathlib.Path(directory)
        if not path.exists():
            os.makedirs(path, exist_ok=True)
