from io import FileIO, StringIO
from textwrap import dedent
from unittest import TestCase

from ivoire import transform
from ivoire.tests.util import PatchMixin, mock


FAKE_MODULE, FAKE_PATH = "a_module", "a/path"


def importer(module=FAKE_MODULE, path=FAKE_PATH):
    with mock.patch.object(transform, "is_spec", lambda path : True):
        return transform.ExampleImporter(module, path)


class TestLoad(TestCase, PatchMixin):
    def test_load_module_is_exposed_globally(self):
        ExampleImporter = self.patchObject(transform, "ExampleImporter")
        path = FAKE_PATH

        module = transform.load(path)

        ExampleImporter.assert_called_once_with(path)
        self.assertEqual(
            module, ExampleImporter.return_value.load_module.return_value,
        )


class TestInstall(TestCase, PatchMixin):
    def test_adds_loader_to_path_hooks(self):
        hooks = self.patchObject(transform.sys, "path_hooks", [next])
        transform.ExampleImporter.register()
        self.assertEqual(hooks, [next, transform.ExampleImporter])


class TestUninstall(TestCase, PatchMixin):
    def test_removes_loader_from_path_hooks(self):
        hooks = self.patchObject(
            transform.sys, "path_hooks", [next, transform.ExampleImporter]
        )
        transform.ExampleImporter.unregister()
        self.assertEqual(hooks, [next])


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


class TestModuleLoading(TestCase, PatchMixin):
    def setUp(self):
        self.importer = importer()
        self.parse = self.patchObject(transform.ast, "parse")
        self.source = mock.Mock()

    def test_it_transforms_the_source(self):
        Transformer = self.patchObject(transform, "ExampleTransformer")
        visit = Transformer.return_value.visit

        transformed = self.importer.transform(self.source)
        self.assertEqual(transformed, visit.return_value)
        self.parse.assert_called_once_with(self.source)


class TestExampleTransformer(TestCase, PatchMixin):
    def setUp(self):
        self.transformer = transform.ExampleTransformer()
        self.source = dedent("""
        from ivoire import describe

        with describe(next) as it:
            with it("returns the next element") as test:
                test.assertEqual(next(iter([1, 2, 3])), 1)

            with it("raises StopIterations for empty iterables") as test:
                with test.assertRaises(StopIteration):
                    next(iter([]))

        with describe(range) as it:
            with it("builds a range of integers") as test:
                test.assertEqual(range(3), [0, 1, 2])
        """)
