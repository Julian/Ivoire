from unittest import TestCase, skipIf

import ivoire
from ivoire import result, run
from ivoire.tests.util import PatchMixin, mock


class TestParser(TestCase, PatchMixin):
    def test_dots_by_default(self):
        should_color = self.patchObject(run, "should_color")
        arguments = run.parse(["foo"])
        self.assertEqual(arguments.Formatter, result.DotsFormatter)

    def test_not_verbose_by_default(self):
        arguments = run.parse(["foo"])
        self.assertFalse(arguments.verbose)

    def test_colored_auto_by_default(self):
        should_color = self.patchObject(run, "should_color")
        arguments = run.parse(["foo"])
        should_color.assert_called_once_with("auto")

    def test_color(self):
        should_color = self.patchObject(run, "should_color")
        arguments = run.parse(["--color=auto", "foo"])
        self.assertEqual(arguments.color, should_color.return_value)
        should_color.assert_called_once_with("auto")

    def test_not_exitfirst_by_default(self):
        arguments = run.parse(["foo"])
        self.assertFalse(arguments.exitfirst)

    def test_exitfirst(self):
        arguments = run.parse(["--exitfirst", "foo"])
        self.assertTrue(arguments.exitfirst)

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


class TestRun(TestCase, PatchMixin):
    def setUp(self):
        self.config = mock.Mock(specs=[])
        self.setup = self.patchObject(run, "setup")
        self.exit = self.patchObject(run.sys, "exit")
        self.result = self.patchObject(ivoire, "current_result")

    def test_it_sets_up_the_environment(self):
        run.run(self.config)
        self.setup.assert_called_once_with(self.config)

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
        argv = mock.Mock()

        run.main(argv)

        parse.assert_called_once_with(argv)
        parse.return_value.func.assert_called_once_with(parse.return_value)
