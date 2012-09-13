from unittest import TestCase, skipIf

import ivoire
from ivoire import result, run
from ivoire.tests.util import PatchMixin, mock


class TestColor(TestCase, PatchMixin):
    def setUp(self):
        self.stdout = self.patchObject(run.sys, "stdout")

    def test_auto_is_always_when_connected_to_a_tty(self):
        self.stdout.isatty.return_value = True
        self.assertTrue(run.should_color("auto"))

    def test_auto_is_never_otherwise(self):
        self.stdout.isatty.return_value = False
        self.assertFalse(run.should_color("auto"))


class TestSetup(TestCase, PatchMixin):
    def setUp(self):
        self.patchObject(ivoire, "current_result", None)
        self.config = mock.Mock()

    def test_it_sets_a_result(self):
        run.setup(self.config)
        self.assertIsNotNone(ivoire.current_result)

    def test_it_respects_fail_fast(self):
        self.config.exitfirst = True
        run.setup(self.config)
        self.assertTrue(ivoire.current_result.failfast)

    def test_colored(self):
        self.patchObject(run, "should_color", return_value=True)
        run.setup(self.config)
        self.assertIsInstance(ivoire.current_result.formatter, result.Colored)

    def test_uncolored(self):
        self.patchObject(run, "should_color", return_value=False)
        run.setup(self.config)
        self.assertIsInstance(
            ivoire.current_result.formatter, result.Formatter
        )


class TestMain(TestCase, PatchMixin):
    def setUp(self):
        self.arguments = mock.Mock()
        self.parser = self.patchObject(run, "parser")
        self.setup = self.patchObject(run, "setup")
        self.run = self.patchObject(run, "run")
        self.transform = self.patchObject(run, "transform")

    def test_transform(self):
        self.parser.parse_args.return_value.transform = True
        run.main(self.arguments)
        self.setup.assert_called_once_with(self.parser.parse_args.return_value)
        self.transform.assert_called_once_with(
            self.parser.parse_args.return_value
        )

    def test_runs_setup_and_run(self):
        self.parser.parse_args.return_value.transform = False
        run.main(self.arguments)
        self.setup.assert_called_once_with(self.parser.parse_args.return_value)
        self.run.assert_called_once_with(self.parser.parse_args.return_value)


@skipIf(
    run.ExampleImporter is None, "Transformation not enabled."
)
class TestTransform(TestCase, PatchMixin):
    def setUp(self):
        self.path = "a/path"
        self.config = mock.Mock()
        self.config.transform = True
        self.config.FilePathsOrFQNs = [self.path]
        self.run_path = self.patchObject(run.runpy, "run_path")

    def test_sets_up_path_hook(self):
        ExampleImporter = self.patchObject(run, "ExampleImporter")
        run.transform(self.config)
        ExampleImporter.register.assert_called_once_with()

    def test_runs_the_script(self):
        run.transform(self.config)
        self.run_path.assert_called_once_with(self.path)


class TestRun(TestCase, PatchMixin):
    def setUp(self):
        self.imp = self.patchObject(run, "imp")
        self.importfn = self.patchObject(run, "__import__", create=True)
        self.result = self.patchObject(ivoire, "current_result")

    def test_it_starts_and_stops_a_test_run(self):
        run.run(mock.Mock(FilePathsOrFQNs=[]))
        self.result.startTestRun.assert_called_once_with()
        self.result.stopTestRun.assert_called_once_with()

    def test_parses_and_loads_specs(self):
        cfg = mock.Mock(FilePathsOrFQNs=["foo.bar", "foo/bar/baz.py", "foo"])

        run.run(cfg)

        self.assertEqual(
            self.importfn.mock_calls, [mock.call("foo.bar"), mock.call("foo")],
        )
        self.imp.load_source.assert_called_once_with("baz", "foo/bar/baz.py")
