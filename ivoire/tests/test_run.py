from unittest import TestCase, skipIf

import ivoire
from ivoire import result, run
from ivoire.tests.util import PatchMixin, mock


class TestSetup(TestCase, PatchMixin):
    def setUp(self):
        self.patchObject(ivoire, "current_result", None)
        self.config = mock.Mock(verbose=False, color=False)

    def test_it_sets_a_result(self):
        run.setup(self.config)
        self.assertIsNotNone(ivoire.current_result)

    def test_plain(self):
        self.config.color = False
        run.setup(self.config)
        self.assertEqual(
            ivoire.current_result.formatter, self.config.Formatter.return_value
        )

    def test_verbose(self):
        self.config.verbose = True
        run.setup(self.config)
        self.assertIsInstance(ivoire.current_result.formatter, result.Verbose)

    def test_colored(self):
        self.config.color = True
        run.setup(self.config)
        self.assertIsInstance(ivoire.current_result.formatter, result.Colored)


class TestTransform(TestCase, PatchMixin):
    def setUp(self):
        self.ExampleLoader = self.patchObject(run, "ExampleLoader")
        self.patchObject(run, "transform_possible", True)
        self.config = mock.Mock(runner="runner", specs=["a/spec.py"], args=[])
        self.run_path = self.patchObject(run.runpy, "run_path")

    def test_it_sets_up_path_hook(self):
        run.transform(self.config)
        self.ExampleLoader.register.assert_called_once_with()

    def test_it_runs_the_script(self):
        run.transform(self.config)
        self.run_path.assert_called_once_with(
            self.config.runner, run_name="__main__",
        )

    def test_it_cleans_and_resets_sys_argv(self):
        self.config.args = ["foo", "bar", "baz"]
        argv = self.patchObject(run.sys, "argv", ["spam", "eggs"])

        # argv was set immediately before run_path
        self.run_path.side_effect = lambda *a, **k : (
            self.assertEqual(argv[1:], self.config.args)
        )
        run.transform(self.config)

        # ... and was restored afterwards
        self.assertEqual(argv[1:], ["eggs"])
