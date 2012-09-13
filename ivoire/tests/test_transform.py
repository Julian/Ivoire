from textwrap import dedent
from unittest import TestCase, TestLoader
import ast

from ivoire import transform
from ivoire.tests.util import PatchMixin, mock


FAKE_PATH = "a/path"


class TestLoad(TestCase, PatchMixin):
    def test_load_module_is_exposed_globally(self):
        ExampleImporter = self.patchObject(transform, "ExampleImporter")
        path = FAKE_PATH

        module = transform.load(path)

        ExampleImporter.assert_called_once_with(path)
        self.assertEqual(
            module, ExampleImporter.return_value.load_module.return_value,
        )


class TestInstallUninstall(TestCase, PatchMixin):
    def setUp(self):
        self.path_hooks = self.patchObject(transform.sys, "path_hooks", [])

    def test_adds_loader_to_path_hooks(self):
        self.path_hooks.append(next)
        transform.ExampleImporter.register()
        self.assertEqual(self.path_hooks, [next, transform.ExampleImporter])

    def test_removes_loader_from_path_hooks(self):
        self.path_hooks.extend([next, transform.ExampleImporter])
        transform.ExampleImporter.unregister()
        self.assertEqual(self.path_hooks, [next])


class TestFindModules(TestCase, PatchMixin):
    def setUp(self):
        self.is_spec = self.patchObject(transform, "is_spec")
        self.module = "a_module"

    def test_finds_ivoire_modules(self):
        self.is_spec.return_value = True
        importer = transform.ExampleImporter(self.module, FAKE_PATH)

    def test_does_not_find_non_ivoire_modules(self):
        self.is_spec.return_value = False
        with self.assertRaises(ImportError):
            importer = transform.ExampleImporter(self.module, FAKE_PATH)

    def test_importer_is_also_the_loader(self):
        importer = transform.ExampleImporter(self.module, FAKE_PATH)
        loader = importer.find_module("a.module")
        self.assertEqual(loader, importer)


class TestExampleTransformer(TestCase, PatchMixin):
    def setUp(self):
        self.transformer = transform.ExampleTransformer()

    def assertNotTransformed(self, source):
        node = ast.parse(dedent(source))
        transformed = self.transformer.transform(node)
        self.assertIs(node, transformed, "unexpected transformation!")

    def dump(self, node):
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
        except Exception:
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

    def test_it_does_not_transform_other_context_managers(self):
        self.assertNotTransformed("""
            from warnings import catchwarnings
            with catchwarnings() as thing:
                with catchwarnings():
                    pass
        """)
