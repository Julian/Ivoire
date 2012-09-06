from io import FileIO, StringIO
from textwrap import dedent
from unittest import TestCase

from ivoire import transform as ivoire
from ivoire.tests.util import PatchMixin, mock


FAKE_MODULE, FAKE_PATH = "a_module", "a/path"


def importer(module=FAKE_MODULE, path=FAKE_PATH):
    with mock.patch.object(ivoire, "is_ivoire_module", lambda path : True):
        return ivoire.IvoireImporter(module, path)


class TestInstall(TestCase, PatchMixin):
    def test_adds_loader_to_path_hooks(self):
        hooks = self.patchObject(ivoire.sys, "path_hooks", [next])
        ivoire.IvoireImporter.register()
        self.assertEqual(hooks, [next, ivoire.IvoireImporter])


class TestUninstall(TestCase, PatchMixin):
    def test_removes_loader_from_path_hooks(self):
        hooks = self.patchObject(
            ivoire.sys, "path_hooks", [next, ivoire.IvoireImporter]
        )
        ivoire.IvoireImporter.unregister()
        self.assertEqual(hooks, [next])


class TestFindModules(TestCase, PatchMixin):
    def setUp(self):
        self.is_ivoire_module = self.patchObject(ivoire, "is_ivoire_module")
        self.module = "a_module"

    def test_finds_ivoire_modules(self):
        self.is_ivoire_module.return_value = True
        importer = ivoire.IvoireImporter(self.module, FAKE_PATH)

    def test_does_not_find_non_ivoire_modules(self):
        self.is_ivoire_module.return_value = False
        with self.assertRaises(ImportError):
            importer = ivoire.IvoireImporter(self.module, FAKE_PATH)

    def test_importer_is_also_the_loader(self):
        importer = ivoire.IvoireImporter(self.module, FAKE_PATH)
        loader = importer.find_module("a.module")
        self.assertEqual(loader, importer)


class TestLoad(TestCase, PatchMixin):
    def test_load_module_is_exposed_globally(self):
        IvoireImporter = self.patchObject(ivoire, "IvoireImporter")
        path = FAKE_PATH

        module = ivoire.load(path)

        IvoireImporter.assert_called_once_with(path)
        self.assertEqual(
            module, IvoireImporter.return_value.load_module.return_value,
        )


class TestIsIvoireModule(TestCase, PatchMixin):
    def set_module(self, contents):
        module = StringIO(contents)
        file_object = mock.MagicMock(spec=FileIO)
        file_object.__enter__.return_value = module
        self.patchObject(ivoire, "open", create=True, return_value=file_object)

    def test_things_that_from_import_ivoire_are_ivoire_modules(self):
        self.set_module("from ivoire import describe")
        self.assertTrue(ivoire.is_ivoire_module(FAKE_PATH))

    def test_things_that_import_ivoire_are_ivoire_modules(self):
        self.set_module("import ivoire")
        self.assertTrue(ivoire.is_ivoire_module(FAKE_PATH))

    def test_things_that_dont_import_ivoire_arent_an_ivoire_module(self):
        self.set_module("import sys")
        self.assertFalse(ivoire.is_ivoire_module(FAKE_PATH))


class TestModuleLoading(TestCase, PatchMixin):
    def setUp(self):
        self.importer = importer()
        self.module = dedent("""
        from ivoire import describe
        """)

    def test_transforms_module(self):
        pass
