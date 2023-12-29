from io import StringIO
import sys

from ivoire import describe, result
from ivoire.spec.util import ExampleWithPatch, mock


def fake_exc_info():
    try:
        raise Exception("Used to construct exc_info")
    except Exception:
        return sys.exc_info()


with describe(result.ExampleResult, Example=ExampleWithPatch) as it:

    @it.before
    def before(test):
        test.formatter = mock.Mock()
        test.result = result.ExampleResult(test.formatter)
        test.test = mock.Mock()
        test.exc_info = fake_exc_info()

    def assertShown(test, output):
        test.formatter.show.assert_called_with(output)

    with it("enters groups") as test:
        test.result.enterGroup(test.test.group)
        test.formatter.enter_group.assert_called_once_with(test.test.group)
        assertShown(test, test.formatter.enter_group.return_value)

    with it("exits groups") as test:
        test.result.exitGroup(test.test.group)
        test.formatter.exit_group.assert_called_once_with(test.test.group)
        assertShown(test, test.formatter.exit_group.return_value)

    with it("shows successes") as test:
        test.result.addSuccess(test.test)
        test.formatter.success.assert_called_once_with(test.test)
        assertShown(test, test.formatter.success.return_value)

    with it("shows errors") as test:
        test.result.addError(test.test, test.exc_info)
        test.formatter.error.assert_called_once_with(test.test, test.exc_info)
        assertShown(test, test.formatter.error.return_value)

    with it("shows failures") as test:
        test.result.addFailure(test.test, test.exc_info)
        test.formatter.failure.assert_called_once_with(
            test.test,
            test.exc_info,
        )
        assertShown(test, test.formatter.failure.return_value)

    with it("shows skips") as test:
        test.result.addSkip(test.test, "a reason")
        test.formatter.skip.assert_called_once_with(test.test, "a reason")
        assertShown(test, test.formatter.skip.return_value)

    with it("shows statistics and non-successes") as test:
        test.result.startTestRun()
        test.result.stopTestRun()

        elapsed = test.result.elapsed

        test.formatter.assert_has_calls(
            [
                mock.call.finished(),
                mock.call.errors(test.result.errors),
                mock.call.show(test.formatter.errors.return_value),
                mock.call.failures(test.result.failures),
                mock.call.show(test.formatter.failures.return_value),
                mock.call.statistics(elapsed=elapsed, result=test.result),
                mock.call.show(test.formatter.statistics.return_value),
            ],
        )

    with it("times the example run") as test:
        start, end = [1.234567, 8.9101112]
        test.patchObject(result.time, "time", side_effect=[start, end])

        test.result.startTestRun()
        test.result.stopTestRun()

        test.assertEqual(test.result.elapsed, end - start)


with describe(result.Verbose, Example=ExampleWithPatch) as it:

    @it.before
    def before(test):
        test.exc_info = mock.Mock()
        test.formatter = mock.Mock()
        test.result = mock.Mock()
        test.test = mock.Mock()
        test.verbose = result.Verbose(test.formatter)

    with it("delegates to the formatter") as test:
        test.assertEqual(test.verbose.foo, test.formatter.foo)

    with it("finishes with a newline") as test:
        test.verbose.finished()
        test.formatter.show.assert_called_once_with("\n")

    with it("shows group names when entered") as test:
        test.assertEqual(
            test.verbose.enter_group(test.test.group),
            f"{test.test.group}\n",
        )

    with it("formats successes") as test:
        test.assertEqual(
            test.verbose.success(test.test),
            f"    {test.test}\n",
        )

    with it("formats errors") as test:
        test.assertEqual(
            test.verbose.error(test.test, test.exc_info),
            f"    {test.test} - ERROR\n",
        )

    with it("formats failures") as test:
        test.assertEqual(
            test.verbose.failure(test.test, test.exc_info),
            f"    {test.test} - FAIL\n",
        )


with describe(result.DotsFormatter, Example=ExampleWithPatch) as it:

    @it.before
    def before(test):
        test.elapsed = 1.23456789
        test.result = mock.Mock()
        test.test = mock.Mock()
        test.exc_info = fake_exc_info()

        test.stream = mock.Mock()
        test.formatter = result.DotsFormatter(test.stream)

    with it("does not format anything for entering a group") as test:
        test.assertFalse(test.formatter.enter_group(test.test.group))

    with it("does not format anything for exiting a group") as test:
        test.assertFalse(test.formatter.exit_group(test.test.group))

    with it("formats . for successes") as test:
        test.assertEqual(test.formatter.success(test.test), ".")

    with it("formats E for errors") as test:
        test.assertEqual(test.formatter.error(test.test, test.exc_info), "E")

    with it("formats F for failures") as test:
        test.assertEqual(test.formatter.failure(test.test, test.exc_info), "F")

    with it("formats S for skips") as test:
        test.assertEqual(test.formatter.skip(test.test, test.exc_info), "S")

    with it("formats a summary message") as test:
        test.result.testsRun = 20
        test.result.errors = range(8)
        test.result.failures = range(2)

        test.assertEqual(
            test.formatter.result_summary(test.result),
            "20 examples, 8 errors, 2 failures\n",
        )

    with it("formats a timing message") as test:
        test.assertEqual(
            test.formatter.timing(test.elapsed),
            f"Finished in {test.elapsed:.6f} seconds.\n",
        )

    with it("formats tracebacks") as test:
        example = mock.MagicMock()
        example.__str__.return_value = "Example"  # type: ignore[attr-defined]
        traceback = "The\nTraceback\n"

        test.assertEqual(
            test.formatter.traceback(example, traceback),
            "\n".join([str(example), traceback]),
        )


with describe(result.DotsFormatter.show, Example=ExampleWithPatch) as it:

    @it.before
    def before(test):
        test.stream = StringIO()
        test.formatter = result.DotsFormatter(test.stream)

    with it("writes to stderr by default") as test:
        test.assertEqual(result.DotsFormatter().stream, sys.stderr)

    with it("writes and flushes") as test:
        test.stream.flush = mock.Mock()
        test.formatter.show("hello\n")
        test.assertEqual(test.stream.getvalue(), "hello\n")
        test.assertTrue(test.stream.flush.called)
