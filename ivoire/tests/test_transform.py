from __future__ import print_function
from textwrap import dedent
from unittest import TestCase, TestLoader, skipIf
import ast

from ivoire import transform
from ivoire.tests.util import PatchMixin, mock


class TestLoad(TestCase, PatchMixin):
    def test_load_module_is_exposed_globally(self):
        ExampleLoader = self.patchObject(transform, "ExampleLoader")
        path = "dummy/path"

        module = transform.load_spec(path)

        ExampleLoader.assert_called_once_with(path)
        self.assertEqual(
            module, ExampleLoader.return_value.load_module.return_value,
        )


class TestRegistration(TestCase, PatchMixin):
    def setUp(self):
        self.FileFinder = self.patchObject(transform, "FileFinder")
        self.hooks = ()
        self.path_hooks = self.patchObject(
            transform.sys, "path_hooks", list(self.hooks)
        )

    def test_it_registers_a_file_finder(self):
        transform.ExampleLoader.register()
        self.assertEqual(
            self.path_hooks,
            list(self.hooks) + [self.FileFinder.path_hook.return_value],
        )
        self.FileFinder.path_hook.assert_called_once_with(
            (transform.ExampleLoader, ["_spec.py"]),
        )

    def test_it_unregisters_the_file_finder(self):
        transform.ExampleLoader.register()
        transform.ExampleLoader.unregister()
        self.assertEqual(self.path_hooks, list(self.hooks))


class TestExampleTransformer(TestCase, PatchMixin):
    def setUp(self):
        self.transformer = transform.ExampleTransformer()

    def assertNotTransformed(self, source):
        node = ast.parse(dedent(source))
        transformed = self.transformer.transform(node)
        self.assertIs(node, transformed, "unexpected transformation!")

    def dump(self, node):  # pragma: no cover
        print(
            "\n--- Dumping Node ---\n",
            ast.dump(node),
            "\n--- End ---",
            sep="\n"
        )

    def execute(self, source):
        self.globals, self.locals = {}, {}
        self.node = ast.parse(dedent(source))
        self.transformed = self.transformer.transform(self.node)
        compiled = compile(self.transformed, "<testing transform>", "exec")

        try:
            exec(compiled, self.globals, self.locals)
        except Exception:  # pragma: no cover
            self.dump(self.transformed)
            raise

    def test_it_fixes_missing_linenos(self):
        fix = self.patchObject(transform.ast, "fix_missing_locations")
        node = ast.Pass()
        self.transformer.transform(node)
        fix.assert_called_once_with(node)

    def test_it_transforms_ivoire_imports_to_unittest(self):
        self.execute("from ivoire import describe")
        self.assertEqual(self.locals, {"TestCase" : TestCase})

    def test_it_does_not_transform_other_imports_to_unittest(self):
        self.assertNotTransformed("from textwrap import dedent")

    @skipIf(
        not transform.possible,
        "Transformation isn't supported yet on this version.",
    )
    def test_it_transforms_uses_of_describe_to_test_cases(self):
        self.execute("""
            from ivoire import describe
            with describe(next) as it:
                with it("returns the next element") as test:
                    test.i = [1, 2, 3]
                    test.assertEqual(next(test.i), 1)
        """)

        TestNext = self.locals["TestNext"]
        test = TestNext("test_it_returns_the_next_element")
        test.run()
        self.assertEqual(test.i, [1, 2, 3])

    @skipIf(
        not transform.possible,
        "Transformation isn't supported yet on this version.",
    )
    def test_it_does_not_transform_other_context_managers(self):
        self.assertNotTransformed("""
            from warnings import catchwarnings
            with catchwarnings() as thing:
                with catchwarnings():
                    pass
        """)
