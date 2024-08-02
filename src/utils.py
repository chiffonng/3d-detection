"""Utility functions for the project."""

from pathlib import Path

# root/src/some_module.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def get_absolute_path(path_from_root: str) -> Path:
    """Get the absolute path of a file.

    Args:
        path_from_root (str): The file path compared to the project root.

    Returns:
        Path: The absolute path of the file.
    """
    return PROJECT_ROOT / path_from_root


def has_file_ext(directory: Path, file_extension: str) -> bool:
    """Check if a directory contains at least one file with the given extension.

    Args:
        directory (Path): The directory compared to the project root.
        file_extension (str): The file extension to look for.

    Returns:
        bool: True if the directory is empty, False otherwise.
    """
    dir_abspath = get_absolute_path(directory)
    return not any(dir_abspath.glob(f"*{file_extension}"))
