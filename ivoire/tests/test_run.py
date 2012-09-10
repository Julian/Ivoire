from unittest import TestCase

import ivoire
from ivoire import result, run
from ivoire.tests.util import PatchMixin, mock


class TestColor(TestCase, PatchMixin):
    def test_auto_is_always_when_connected_to_a_tty(self):
        self.patchObject(run.sys.stdout, "isatty", return_value=True)
        self.assertTrue(run.should_color("auto"))

    def test_auto_is_never_otherwise(self):
        self.patchObject(run.sys.stdout, "isatty", return_value=False)
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
    def test_parses_and_loads_specs(self):
        imp = self.patchObject(run, "imp")
        importfn = self.patchObject(run, "__import__", create=True)
        cfg = mock.Mock(FilePathsOrFQNs=["foo.bar", "foo/bar/baz.py", "foo"])

        run.run(cfg)

        self.assertEqual(
            importfn.mock_calls, [mock.call("foo.bar"), mock.call("foo")],
        )
        imp.load_source.assert_called_once_with("baz", "foo/bar/baz.py")
