import fnmatch
import imp
import os


def load_by_name(name):
    """
    Load a spec from either a file path or a fully qualified name.

    """

    if os.path.exists(name):
        load_from_path(name)
    else:
        __import__(name)


def load_from_path(path):
    """
    Load a spec from a given path, discovering specs if a directory is given.

    """

    if os.path.isdir(path):
        paths = discover(path)
    else:
        paths = [path]

    for path in paths:
        name = os.path.basename(os.path.splitext(path)[0])
        imp.load_source(name, path)


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
        for spec in filter_specs(filenames):
            yield os.path.join(dirpath, spec)
