from ivoire import describe, load
from ivoire.spec.util import ExampleWithPatch, mock


with describe(load.load_by_name, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.path_exists = test.patchObject(load.os.path, "exists")
        test.load_from_path = test.patchObject(load, "load_from_path")
        test.__import__ = test.patchObject(load, "__import__", create=True)

    with it("loads paths") as test:
        test.path_exists.return_value = True
        load.load_by_name("foo")
        test.load_from_path.assert_called_once_with("foo")

    with it("loads modules") as test:
        test.path_exists.return_value = False
        load.load_by_name("foo")
        test.__import__.assert_called_once_with("foo")


with describe(load.load_from_path, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.isdir = test.patchObject(load.os.path, "isdir")
        test.load_source = test.patchObject(load.imp, "load_source")
        test.path = "foo/bar"

    with it("discovers specs if given a directory") as test:
        test.isdir.return_value = True
        specs = ["foo/bar", "bar/baz", "baz/quux"]
        discover = test.patchObject(load, "discover", return_value=specs)

        load.load_from_path(test.path)

        test.assertEqual(test.load_source.mock_calls, [
            mock.call("bar", "foo/bar"),
            mock.call("baz", "bar/baz"),
            mock.call("quux", "baz/quux"),
        ])

    with it("loads paths") as test:
        test.isdir.return_value = False
        load.load_from_path(test.path)
        test.load_source.assert_called_once_with("bar", test.path)


with describe(load.filter_specs, Example=ExampleWithPatch) as it:
    with it("filters out only specs") as test:
        files = ["a.py", "dir/b.py", "dir/c_spec.py", "d_spec.py"]
        specs = load.filter_specs(files)
        test.assertEqual(specs, ["dir/c_spec.py", "d_spec.py"])


with describe(load.discover, Example=ExampleWithPatch) as it:
    with it("discovers specs") as test:
        subdirs = mock.Mock()
        files, more_files = [mock.Mock()], [mock.Mock(), mock.Mock()]

        tree = [("dir", subdirs, files), ("dir/child", subdirs, more_files)]
        walk = test.patchObject(load.os, "walk", return_value=tree)

        no_filter = mock.Mock(side_effect=lambda paths : paths)

        specs = list(load.discover("a/path", filter_specs=no_filter))

        test.assertEqual(specs, files + more_files)
        test.assertTrue(no_filter.called)
        walk.assert_called_once_with("a/path")
