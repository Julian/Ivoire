from unittest import TestCase, skipIf

import ivoire
from ivoire import result, run
from ivoire.tests.util import PatchMixin, mock


class TestLoadByName(TestCase, PatchMixin):
    def setUp(self):
        self.path_exists = self.patchObject(run.os.path, "exists")

    def test_loads_paths(self):
        self.path_exists.return_value = True
        load_path = self.patchObject(run, "load_from_path")
        run.load_by_name("foo")
        load_path.assert_called_once_with("foo")

    def test_loads_modules(self):
        self.path_exists.return_value = False
        importfn = self.patchObject(run, "__import__", create=True)
        run.load_by_name("foo")
        importfn.assert_called_once_with("foo")


class TestLoadPath(TestCase, PatchMixin):
    def setUp(self):
        self.isdir = self.patchObject(run.os.path, "isdir")
        self.load_source = self.patchObject(run.imp, "load_source")
        self.path = "foo/bar"

    def test_it_discovers_specs_if_given_a_directory(self):
        self.isdir.return_value = True
        specs = ["foo/bar", "bar/baz", "baz/quux"]
        discover = self.patchObject(run, "discover", return_value=specs)

        run.load_from_path(self.path)

        self.assertEqual(self.load_source.mock_calls, [
            mock.call("bar", "foo/bar"),
            mock.call("baz", "bar/baz"),
            mock.call("quux", "baz/quux"),
        ])

    def test_it_loads_paths(self):
        self.isdir.return_value = False
        run.load_from_path(self.path)
        self.load_source.assert_called_once_with("bar", self.path)


class TestDiscovery(TestCase, PatchMixin):
    def test_filters_specs(self):
        files = ["a.py", "dir/b.py", "dir/c_spec.py", "d_spec.py"]
        specs = run.filter_specs(files)
        self.assertEqual(specs, ["dir/c_spec.py", "d_spec.py"])

    def test_discover(self):
        subdirs = mock.Mock()
        files, more_files = [mock.Mock()], [mock.Mock(), mock.Mock()]

        tree = [("dir", subdirs, files), ("dir/child", subdirs, more_files)]
        walk = self.patchObject(run.os, "walk", return_value=tree)

        no_filter = mock.Mock(side_effect=lambda paths : paths)

        specs = list(run.discover("a/path", filter_specs=no_filter))

        self.assertEqual(specs, files + more_files)
        self.assertTrue(no_filter.called)
        walk.assert_called_once_with("a/path")


class TestParser(TestCase, PatchMixin):
    def test_colored_auto_by_default(self):
        should_color = self.patchObject(run, "should_color")
        arguments = run.parse(["foo"])
        should_color.assert_called_once_with("auto")

    def test_color(self):
        should_color = self.patchObject(run, "should_color")
        arguments = run.parse(["--color=auto", "foo"])
        self.assertEqual(arguments.color, should_color.return_value)
        should_color.assert_called_once_with("auto")

    def test_no_transform(self):
        arguments = run.parse(["foo", "bar"])
        self.assertEqual(arguments.func, run.run)
        self.assertEqual(arguments.specs, ["foo", "bar"])

    def test_transform(self):
        arguments = run.parse(["transform", "foo", "bar"])
        self.assertEqual(arguments.func, run.transform)
        self.assertEqual(arguments.runner, "foo")
        self.assertEqual(arguments.args, ["bar"])

    def test_does_not_break_on_empty_args(self):
        # Didn't think of the proper way to test this yet so this test will
        # ultimately probably break
        argv = self.patchObject(run.sys, "argv", ["ivoire"])  #  sowwy
        parse_args = self.patchObject(run._parser, "parse_args")  #  sowwy
        run.parse()
        parse_args.assert_called_once_with(["run"])


class TestColor(TestCase, PatchMixin):
    def setUp(self):
        self.stderr = self.patchObject(run.sys, "stderr")

    def test_auto_is_always_when_connected_to_a_tty(self):
        self.stderr.isatty.return_value = True
        self.assertTrue(run.should_color("auto"))

    def test_auto_is_never_otherwise(self):
        self.stderr.isatty.return_value = False
        self.assertFalse(run.should_color("auto"))


class TestSetup(TestCase, PatchMixin):
    def setUp(self):
        self.patchObject(ivoire, "current_result", None)
        self.config = mock.Mock()

    def test_it_sets_a_result(self):
        run.setup(self.config)
        self.assertIsNotNone(ivoire.current_result)

    def test_colored(self):
        self.config.color = True
        run.setup(self.config)
        self.assertIsInstance(ivoire.current_result.formatter, result.Colored)

    def test_uncolored(self):
        self.config.color = False
        run.setup(self.config)
        self.assertIsInstance(
            ivoire.current_result.formatter, result.Formatter
        )


class TestTransform(TestCase, PatchMixin):
    def setUp(self):
        self.ExampleLoader = self.patchObject(run, "ExampleLoader")
        self.patchObject(run, "transform_possible", True)
        self.config = mock.Mock(runner="runner", specs=["a/spec.py"])
        self.run_path = self.patchObject(run.runpy, "run_path")

    def test_sets_up_path_hook(self):
        run.transform(self.config)
        self.ExampleLoader.register.assert_called_once_with()

    def test_runs_the_script(self):
        run.transform(self.config)
        self.run_path.assert_called_once_with(self.config.runner)


class TestRun(TestCase, PatchMixin):
    def setUp(self):
        self.config = mock.Mock(specs=[])
        self.imp = self.patchObject(run, "imp")
        self.importfn = self.patchObject(run, "__import__", create=True)
        self.result = self.patchObject(ivoire, "current_result")

    def test_it_respects_fail_fast(self):
        self.config.exitfirst = True
        run.run(self.config)
        self.assertTrue(ivoire.current_result.failfast)

    def test_it_starts_and_stops_a_test_run(self):
        run.run(self.config)
        self.result.startTestRun.assert_called_once_with()
        self.result.stopTestRun.assert_called_once_with()

    def test_it_loads_specs(self):
        load_by_name = self.patchObject(run, "load_by_name")
        self.config.specs = [mock.Mock(), mock.Mock(), mock.Mock()]
        run.run(self.config)
        self.assertEqual(
            load_by_name.mock_calls,
            [mock.call(spec) for spec in self.config.specs],
        )


class TestMain(TestCase, PatchMixin):
    def test_main(self):
        parse = self.patchObject(run, "parse")
        setup = self.patchObject(run, "setup")

        argv = mock.Mock()
        run.main(argv)

        parse.assert_called_once_with(argv)
        setup.assert_called_once_with(parse.return_value)
        parse.return_value.func.assert_called_once_with(parse.return_value)
