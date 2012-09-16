from unittest import TestCase

from ivoire import load
from ivoire.tests.util import PatchMixin, mock

class TestLoadByName(TestCase, PatchMixin):
    def setUp(self):
        self.path_exists = self.patchObject(load.os.path, "exists")

    def test_loads_paths(self):
        self.path_exists.return_value = True
        load_path = self.patchObject(load, "load_from_path")
        load.load_by_name("foo")
        load_path.assert_called_once_with("foo")

    def test_loads_modules(self):
        self.path_exists.return_value = False
        importfn = self.patchObject(load, "__import__", create=True)
        load.load_by_name("foo")
        importfn.assert_called_once_with("foo")


class TestLoadPath(TestCase, PatchMixin):
    def setUp(self):
        self.isdir = self.patchObject(load.os.path, "isdir")
        self.load_source = self.patchObject(load.imp, "load_source")
        self.path = "foo/bar"

    def test_it_discovers_specs_if_given_a_directory(self):
        self.isdir.return_value = True
        specs = ["foo/bar", "bar/baz", "baz/quux"]
        discover = self.patchObject(load, "discover", return_value=specs)

        load.load_from_path(self.path)

        self.assertEqual(self.load_source.mock_calls, [
            mock.call("bar", "foo/bar"),
            mock.call("baz", "bar/baz"),
            mock.call("quux", "baz/quux"),
        ])

    def test_it_loads_paths(self):
        self.isdir.return_value = False
        load.load_from_path(self.path)
        self.load_source.assert_called_once_with("bar", self.path)


class TestDiscovery(TestCase, PatchMixin):
    def test_filters_specs(self):
        files = ["a.py", "dir/b.py", "dir/c_spec.py", "d_spec.py"]
        specs = load.filter_specs(files)
        self.assertEqual(specs, ["dir/c_spec.py", "d_spec.py"])

    def test_discover(self):
        subdirs = mock.Mock()
        files, more_files = [mock.Mock()], [mock.Mock(), mock.Mock()]

        tree = [("dir", subdirs, files), ("dir/child", subdirs, more_files)]
        walk = self.patchObject(load.os, "walk", return_value=tree)

        no_filter = mock.Mock(side_effect=lambda paths : paths)

        specs = list(load.discover("a/path", filter_specs=no_filter))

        self.assertEqual(specs, files + more_files)
        self.assertTrue(no_filter.called)
        walk.assert_called_once_with("a/path")


