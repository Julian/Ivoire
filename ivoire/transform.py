import ast
import sys


from ivoire.compat import FileFinder, SourceFileLoader, transform_possible


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
            describes = context.args[0].id
            example_group_name = withitem.optional_vars.id
            return self.transform_describe(node, describes, example_group_name)
        else:
            return node

    def transform_describe(self, node, describes, context_variable):
        """
        Transform a describe node into a ``TestCase``.

        ``node`` is the node object.
        ``describes`` is the name of the object being described.
        ``context_variable`` is the name bound in the context manager (usually
        "it").

        """

        body = self.transform_describe_body(node.body, context_variable)
        return ast.ClassDef(
            name="Test" + describes.title(),
            bases=[ast.Name(id="TestCase", ctx=ast.Load())],
            keywords=[],
            starargs=None,
            kwargs=None,
            body=list(body),
            decorator_list=[],
        )

    def transform_describe_body(self, body, group_var):
        """
        Transform the body of an ``ExampleGroup``.

        ``body`` is the body.
        ``group_var`` is the name bound to the example group in the context
        manager (usually "it").

        """

        for node in body:
            withitem, = node.items
            context_expr = withitem.context_expr

            name = context_expr.args[0].s
            context_var = withitem.optional_vars.id

            yield self.transform_example(node, name, context_var, group_var)

    def transform_example(self, node, name, context_variable, group_variable):
        """
        Transform an example node into a test method.

        Returns the unchanged node if it wasn't an ``Example``.

        ``node`` is the node object.
        ``name`` is the name of the example being described.
        ``context_variable`` is the name bound in the context manager (usually
        "test").
        ``group_variable`` is the name bound in the surrounding example group's
        context manager (usually "it").

        """

        test_name = "_".join(["test", group_variable] + name.split())
        body = self.transform_example_body(node.body, context_variable)

        return ast.FunctionDef(
            name=test_name,
            args=self.takes_only_self(),
            body=list(body),
            decorator_list=[],
        )

    def transform_example_body(self, body, context_variable):
        """
        Transform the body of an ``Example`` into the body of a method.

        Replaces instances of ``context_variable`` to refer to ``self``.

        ``body`` is the body.
        ``context_variable`` is the name bound in the surrounding context
        manager to the example (usually "test").

        """

        for node in body:
            for child in ast.walk(node):
                if isinstance(child, ast.Name):
                    if child.id == context_variable:
                        child.id = "self"
            yield node


    def takes_only_self(self):
        """
        Return an argument list node that takes only ``self``.

        """

        return ast.arguments(
            args=[ast.arg(arg="self")],
            defaults=[],
            kw_defaults=[],
            kwonlyargs=[],
        )


class ExampleLoader(SourceFileLoader):

    suffix = "_spec.py"

    @classmethod
    def register(cls):
        """
        Register the path hook.

        """

        cls._finder = FileFinder.path_hook((cls, [cls.suffix]))
        sys.path_hooks.append(cls._finder)

    @classmethod
    def unregister(cls):
        """
        Unregister the path hook.

        """

        sys.path_hooks.remove(cls._finder)

    def source_to_code(self, source_bytes, source_path):
        """
        Transform the source code, then return the code object.

        """

        node = ast.parse(source_bytes)
        transformed = ExampleTransformer().transform(node)
        return compile(transformed, source_path, "exec", dont_inherit=True)
