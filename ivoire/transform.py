import ast
import importlib.machinery
import sys

from ivoire.util import is_spec


class ExampleTransformer(ast.NodeTransformer):
    """
    Transform a module that uses Ivoire into one that uses unittest.

    This is highly experimental, and certain to have bugs (including some
    known ones). Right now it is highly strict and will not properly transform
    all possibilities. File issues if you find things that are wrong.

    Note: None of the methods on this object are public API other than the
    ``transform`` method.

    """

    def transform(self, node):
        transformed = self.visit(node)
        ast.fix_missing_locations(transformed)
        return transformed

    def visit_ImportFrom(self, node):
        if node.module == "ivoire":
            node.module = "unittest"
            node.names[0].name = "TestCase"
        return node

    def visit_With(self, node):
        """
        with describe(thing) as it:
            ...

             |
             v

        class TestThing(TestCase):
            ...

        """

        withitem, = node.items
        context = withitem.context_expr

        if context.func.id == "describe":
            return self.transform_describe(context)
        else:
            return node

    def transform_describe(self, context):
        describes = context.args[0].id
        test_case_name = "Test" + describes.title()

        return ast.ClassDef(
            name=test_case_name,
            bases=[ast.Name(id="TestCase", ctx=ast.Load())],
            keywords=[],
            starargs=None,
            kwargs=None,
            body=[ast.Pass()],
            decorator_list=[],
        )



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


def load(path):
    """
    Load an ivoire module from the given path.

    Returns the resulting transformed module.

    """

    return ExampleImporter(path).load_module(path)
