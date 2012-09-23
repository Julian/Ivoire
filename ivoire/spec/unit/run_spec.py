from ivoire import describe, result, run
from ivoire.spec.util import ExampleWithPatch, mock
import ivoire


with describe(run.parse, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.specs = ["a_spec"]

    with it("sets reasonable defaults") as test:
        should_color = test.patchObject(run, "should_color")
        arguments = run.parse(test.specs)
        test.assertEqual(vars(arguments), {
            "Formatter" : result.DotsFormatter,
            "color" : should_color.return_value,
            "exitfirst" : False,
            "specs" : test.specs,
            "func" : run.run,
            "verbose" : False,
        })
        should_color.assert_called_once_with("auto")

    with it("can exitfirst") as test:
        arguments = run.parse(["--exitfirst"] + test.specs)
        test.assertTrue(arguments.exitfirst)

        arguments = run.parse(["-x"] + test.specs)
        test.assertTrue(arguments.exitfirst)

    with it("can be verbose") as test:
        arguments = run.parse(["--verbose"] + test.specs)
        test.assertTrue(arguments.verbose)

        arguments = run.parse(["-v"] + test.specs)
        test.assertTrue(arguments.verbose)

    with it("can transform") as test:
        arguments = run.parse(["transform", "foo", "bar"])
        test.assertEqual(vars(arguments), {
            "runner" : "foo",
            "args" : ["bar"],
            "func" : run.transform,
        })

    with it("runs run on empty args") as test:
        arguments = run.parse()
        test.assertEqual(arguments.func, run.run)


with describe(run.should_color, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.stderr = test.patchObject(run.sys, "stderr")

    with it("colors whenever stderr is a tty") as test:
        test.stderr.isatty.return_value = True
        test.assertTrue(run.should_color("auto"))

    with it("doesn't color otherwise") as test:
        test.stderr.isatty.return_value = False
        test.assertFalse(run.should_color("auto"))


with describe(run.setup, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.patchObject(ivoire, "current_result", None)
        test.config = mock.Mock(verbose=False, color=False)

    with it("sets a result") as test:
        test.assertIsNone(ivoire.current_result)
        run.setup(test.config)
        test.assertIsNotNone(ivoire.current_result)

    with it("makes a plain Formatter if color and verbose are False") as test:
        run.setup(test.config)
        test.assertEqual(
            ivoire.current_result.formatter, test.config.Formatter.return_value
        )

    with it("makes a verbose Formatter if verbose is True") as test:
        test.config.verbose = True
        run.setup(test.config)
        test.assertIsInstance(ivoire.current_result.formatter, result.Verbose)

    with it("makes a colored Formatter if color is True") as test:
        test.config.color = True
        run.setup(test.config)
        test.assertIsInstance(ivoire.current_result.formatter, result.Colored)


with describe(run.run, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.config = mock.Mock(specs=[])
        test.load_by_name = test.patchObject(run, "load_by_name")
        test.result = test.patch("ivoire.current_result", failfast=False)
        test.setup = test.patchObject(run, "setup")
        test.exit = test.patchObject(run.sys, "exit")

    with it("sets up the environment") as test:
        run.run(test.config)
        test.setup.assert_called_once_with(test.config)

    with it("sets failfast on the result") as test:
        test.assertFalse(test.result.failfast)
        test.config.exitfirst = True
        run.run(test.config)
        test.assertTrue(test.result.failfast)

    with it("starts and stops a test run") as test:
        run.run(test.config)
        test.result.startTestRun.assert_called_once_with()
        test.result.stopTestRun.assert_called_once_with()

    with it("loads specs") as test:
        test.config.specs = [mock.Mock(), mock.Mock(), mock.Mock()]
        run.run(test.config)
        test.assertEqual(
            test.load_by_name.mock_calls,
            [mock.call(spec) for spec in test.config.specs],
        )

    with it("succeeds with status code 0") as test:
        test.result.wasSuccessful.return_value = True
        run.run(test.config)
        test.exit.assert_called_once_with(0)

    with it("fails with status code 1") as test:
        test.result.wasSuccessful.return_value = False
        run.run(test.config)
        test.exit.assert_called_once_with(1)

    with it("logs an error to the result if an import fails") as test:
        test.config.specs = ["does.not.exist"]
        test.load_by_name.side_effect = IndexError

        run.run(test.config)

        (example, traceback), _ = test.result.addError.call_args
        test.assertEqual(str(example), "<not in example>")
        test.assertEqual(traceback[0], IndexError)


with describe(run.main, Example=ExampleWithPatch) as it:
    with it("runs the correct func with parsed args") as test:
        parse = test.patchObject(run, "parse")
        argv = mock.Mock()

        run.main(argv)

        parse.assert_called_once_with(argv)
        parse.return_value.func.assert_called_once_with(parse.return_value)


with describe(run.transform, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.patchObject(run, "transform_possible", True)
        test.ExampleLoader = test.patchObject(run, "ExampleLoader")
        test.config = mock.Mock(runner="runner", specs=["a/spec.py"], args=[])
        test.run_path = test.patchObject(run.runpy, "run_path")

    with it("sets up the path hook") as test:
        run.transform(test.config)
        test.ExampleLoader.register.assert_called_once_with()

    with it("runs the script") as test:
        run.transform(test.config)
        test.run_path.assert_called_once_with(
            test.config.runner, run_name="__main__",
        )

    with it("cleans and resets sys.argv") as test:
        test.config.args = ["foo", "bar", "baz"]
        argv = test.patchObject(run.sys, "argv", ["spam", "eggs"])

        # argv was set immediately before run_path
        test.run_path.side_effect = lambda *a, **k : (
            test.assertEqual(argv[1:], test.config.args)
        )
        run.transform(test.config)

        # ... and was restored afterwards
        test.assertEqual(argv[1:], ["eggs"])
