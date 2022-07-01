#!/usr/bin/env python3
from glob import glob
from os import path, sep

__all__ = []

for file_path in glob(path.dirname(__file__) + sep + "*.py"):
    filename = path.basename(file_path)
    if filename == "__init__.py": continue

    __all__.append(filename.replace(".py", ""))