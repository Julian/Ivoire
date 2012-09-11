from unittest import TestCase

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
    def test_runs_setup_and_run(self):
        self.patchObject(run, "parser")
        self.patchObject(run, "setup")
        self.patchObject(run, "run")

        run.main(["foo"])

        run.setup.assert_called_once_with(run.parser.parse_args.return_value)
        run.run.assert_called_once_with(run.parser.parse_args.return_value)


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
