import importlib.machinery
import sys


def is_ivoire_module(path):
    with open(path) as file:
        return any(
            line.startswith(("from ivoire import ", "import ivoire"))
            for line in file
        )


class IvoireImporter(importlib.machinery.SourceFileLoader):
    def __init__(self, fullname, path, *args, **kwargs):
        if not is_ivoire_module(path):
            raise ImportError()
        super(IvoireImporter, self).__init__(fullname, path, *args, **kwargs)

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


def load(path):
    """
    Load an ivoire module from the given path.

    Returns the resulting transformed module.

    """

    return IvoireImporter(path).load_module(path)
