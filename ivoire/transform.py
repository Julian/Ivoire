import ast
import importlib.machinery
import sys

from ivoire.util import is_spec


class ExampleTransformer(ast.NodeTransformer):
    pass


class ExampleImporter(importlib.machinery.SourceFileLoader):
    def __init__(self, fullname, path, *args, **kwargs):
        if not is_spec(path):
            raise ImportError()
        super(ExampleImporter, self).__init__(fullname, path, *args, **kwargs)

    @classmethod
    def register(cls):
        """
        Register the path hook.

        """

        sys.path_hooks.append(cls)

    @classmethod
    def unregister(cls):
        """
        Unregister the path hook.

        """

        sys.path_hooks.remove(cls)

    def find_module(self, fullname, path=None):
        return self

    def transform(self, source):
        """
        Transform all the ``ExampleGroup``s and ``Example``s in the source.

        """

        node = ast.parse(source)
        return ExampleTransformer().visit(node)


def load(path):
    """
    Load an ivoire module from the given path.

    Returns the resulting transformed module.

    """

    return ExampleImporter(path).load_module(path)
