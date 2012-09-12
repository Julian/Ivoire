from io import FileIO, StringIO
from textwrap import dedent
from unittest import TestCase

from ivoire import transform
from ivoire.tests.util import PatchMixin, mock


FAKE_MODULE, FAKE_PATH = "a_module", "a/path"


def importer(module=FAKE_MODULE, path=FAKE_PATH):
    with mock.patch.object(transform, "is_spec", lambda path : True):
        return transform.IvoireImporter(module, path)


class TestInstall(TestCase, PatchMixin):
    def test_adds_loader_to_path_hooks(self):
        hooks = self.patchObject(transform.sys, "path_hooks", [next])
        transform.IvoireImporter.register()
        self.assertEqual(hooks, [next, transform.IvoireImporter])


class TestUninstall(TestCase, PatchMixin):
    def test_removes_loader_from_path_hooks(self):
        hooks = self.patchObject(
            transform.sys, "path_hooks", [next, transform.IvoireImporter]
        )
        transform.IvoireImporter.unregister()
        self.assertEqual(hooks, [next])


class TestFindModules(TestCase, PatchMixin):
    def setUp(self):
        self.is_spec = self.patchObject(transform, "is_spec")
        self.module = "a_module"

    def test_finds_ivoire_modules(self):
        self.is_spec.return_value = True
        importer = transform.IvoireImporter(self.module, FAKE_PATH)

    def test_does_not_find_non_ivoire_modules(self):
        self.is_spec.return_value = False
        with self.assertRaises(ImportError):
            importer = transform.IvoireImporter(self.module, FAKE_PATH)

    def test_importer_is_also_the_loader(self):
        importer = transform.IvoireImporter(self.module, FAKE_PATH)
        loader = importer.find_module("a.module")
        self.assertEqual(loader, importer)


class TestLoad(TestCase, PatchMixin):
    def test_load_module_is_exposed_globally(self):
        IvoireImporter = self.patchObject(transform, "IvoireImporter")
        path = FAKE_PATH

        module = transform.load(path)

        IvoireImporter.assert_called_once_with(path)
        self.assertEqual(
            module, IvoireImporter.return_value.load_module.return_value,
        )


class TestModuleLoading(TestCase, PatchMixin):
    def setUp(self):
        self.importer = importer()
        self.module = dedent("""
        from ivoire import describe
        """)

    def test_transforms_module(self):
        pass
