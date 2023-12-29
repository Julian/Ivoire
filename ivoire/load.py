"""
Loaders for Ivoire specs.
"""
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType
import fnmatch
import os


def load_by_name(name):
    """
    Load a spec from either a file path or a fully qualified name.
    """
    if Path(name).exists():
        load_from_path(name)
    else:
        __import__(name)


def load_from_path(path):
    """
    Load a spec from a given path, discovering specs if a directory is given.
    """
    paths = discover(path) if Path(path).is_dir() else [path]

    for path in paths:
        name = Path(path).stem
        loader = SourceFileLoader(name, path)
        loader.exec_module(ModuleType(loader.name))


def filter_specs(paths):
    """
    Filter out only the specs from the given (flat iterable of) paths.
    """
    return fnmatch.filter(paths, "*_spec.py")


def discover(path, filter_specs=filter_specs):
    """
    Discover all of the specs recursively inside ``path``.

    Successively yields the (full) relative paths to each spec.
    """
    for dirpath, _, filenames in os.walk(path):
        dirpath = Path(dirpath)
        for spec in filter_specs(filenames):
            yield os.fspath(dirpath / spec)
