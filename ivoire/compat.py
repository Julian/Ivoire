"""
Various crude backports (mostly direct copying) of things from later versions.

"""

try:
    from textwrap import indent
except ImportError:
    # Copied for <3.3

    def indent(text, prefix, predicate=None):
        """Adds 'prefix' to the beginning of selected lines in 'text'.

        If 'predicate' is provided, 'prefix' will only be added to the lines
        where 'predicate(line)' is True. If 'predicate' is not provided,
        it will default to adding 'prefix' to all non-empty lines that do not
        consist solely of whitespace characters.
        """
        if predicate is None:
            def predicate(line):
                return line.strip()

        def prefixed_lines():
            for line in text.splitlines(True):
                yield (prefix + line if predicate(line) else line)
        return ''.join(prefixed_lines())


try:
    from importlib.machinery import FileFinder, SourceFileLoader
except (AttributeError, ImportError):
    FileFinder = SourceFileLoader = object
else:
    if not hasattr(SourceFileLoader, "source_to_code"):  # pre-3.4
        class SourceFileLoader(SourceFileLoader):
            def source_to_code(self, source_bytes, source_path):
                pass
finally:
    transform_possible = SourceFileLoader is not object
