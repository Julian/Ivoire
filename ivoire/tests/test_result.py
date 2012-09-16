from __future__ import unicode_literals
from io import StringIO
from unittest import TestCase
import sys

from ivoire import result
from ivoire.compat import indent
from ivoire.tests.util import PatchMixin, mock


def fake_exc_info():
    try:
        raise Exception("Used to construct exc_info")
    except Exception:
        return sys.exc_info()


class TestExampleResult(TestCase, PatchMixin):
    def setUp(self):
        self.formatter = mock.Mock()
        self.result = result.ExampleResult(self.formatter)
        self.test = mock.Mock()
        self.exc_info = fake_exc_info()

    def assertShown(self, output):
        self.formatter.show.assert_has_call(output)

    def test_times_the_run(self):
        start, end = [1.234567, 8.9101112]
        self.patchObject(result.time, "time", side_effect=[start, end])

        self.result.startTestRun()
        self.result.stopTestRun()

        self.assertEqual(self.result.elapsed, end - start)

    def test_shows_successes(self):
        self.result.addSuccess(self.test)
        self.formatter.success.assert_called_once_with(self.test)
        self.assertShown(self.formatter.success.return_value)

    def test_shows_errors(self):
        self.result.addError(self.test, self.exc_info)
        self.formatter.error.assert_called_once_with(self.test, self.exc_info)
        self.assertShown(self.formatter.error.return_value)

    def test_shows_failures(self):
        self.result.addFailure(self.test, self.exc_info)
        self.formatter.failure.assert_called_once_with(
            self.test, self.exc_info
        )
        self.assertShown(self.formatter.failure.return_value)

    def test_shows_statistics_and_non_successes(self):
        self.result.startTestRun()
        self.result.stopTestRun()

        elapsed = self.result.elapsed

        self.formatter.assert_has_calls([
            mock.call.finished(),
            mock.call.errors(self.result.errors),
            mock.call.show(self.formatter.errors.return_value),
            mock.call.failures(self.result.failures),
            mock.call.show(self.formatter.failures.return_value),
            mock.call.statistics(elapsed=elapsed, result=self.result),
            mock.call.show(self.formatter.statistics.return_value),
        ])


class TestFormatterMixin(TestCase, PatchMixin):
    class Formatter(mock.Mock, result.FormatterMixin):
        pass

    def setUp(self):
        self.formatter = self.Formatter()

    def test_finished(self):
        self.formatter.show = mock.Mock()
        self.formatter.finished()
        self.formatter.show.assert_called_once_with("\n\n")

    def test_errors(self):
        self.formatter.traceback.side_effect = ["a\nb\n", "c\nd\n"]
        errors = [(mock.Mock(), mock.Mock()), (mock.Mock(), mock.Mock())]
        self.assertEqual(
            self.formatter.errors(errors), "Errors:\n\na\nb\n\nc\nd\n\n"
        )

    def test_failures(self):
        self.formatter.traceback.side_effect = ["a\nb\n", "c\nd\n"]
        failures = [(mock.Mock(), mock.Mock()), (mock.Mock(), mock.Mock())]
        self.assertEqual(
            self.formatter.failures(failures), "Failures:\n\na\nb\n\nc\nd\n\n"
        )

    def test_return_nothing_if_no_errors(self):
        self.assertEqual("", self.formatter.errors([]))
        self.assertFalse("", self.formatter.failures([]))

    def test_statistics(self):
        elapsed, result = mock.Mock(), mock.Mock()
        timing_output = self.formatter.timing.return_value = "timing\n"
        result_output = self.formatter.result_summary.return_value = "result\n"

        stats = self.formatter.statistics(elapsed=elapsed, result=result)
        self.assertEqual(stats, "\n".join([timing_output, result_output]))


class TestColored(TestCase, PatchMixin):
    def setUp(self):
        self.exc_info = mock.Mock()
        self.formatter = mock.Mock()
        self.result = mock.Mock()
        self.test = mock.Mock()
        self.colored = result.Colored(self.formatter)

    def test_it_delegates_to_the_formatter(self):
        self.assertEqual(self.colored.foo, self.formatter.foo)

    def test_it_can_color_things(self):
        self.assertEqual(
            self.colored.color("green", "hello"),
            self.colored.ANSI["green"] + "hello" + self.colored.ANSI["reset"],
        )

    def test_it_colors_successes_green(self):
        self.formatter.success.return_value = "S"
        self.assertEqual(
            self.colored.success(self.test), self.colored.color("green", "S"),
        )

    def test_it_colors_failures_red(self):
        self.formatter.failure.return_value = "F"
        self.assertEqual(
            self.colored.failure(self.test, self.exc_info),
            self.colored.color("red", "F"),
        )

    def test_it_colors_errors_red(self):
        self.formatter.error.return_value = "E"
        self.assertEqual(
            self.colored.error(self.test, self.exc_info),
            self.colored.color("red", "E"),
        )

    def test_it_colors_result_green_when_successful(self):
        self.result.wasSuccessful.return_value = True
        self.formatter.result_summary.return_value = "results"
        self.assertEqual(
            self.colored.result_summary(self.result),
            self.colored.color("green", "results"),
        )

    def test_it_colors_result_red_when_unsuccessful(self):
        self.result.wasSuccessful.return_value = False
        self.formatter.result_summary.return_value = "results"
        self.assertEqual(
            self.colored.result_summary(self.result),
            self.colored.color("red", "results"),
        )

    def test_it_colors_example_names_blue_in_tracebacks(self):
        example = mock.MagicMock()
        example.__str__.return_value = "Example"
        example.group.__str__.return_value = "Thing"
        traceback = "The\nTraceback\n"

        name = self.colored.color("blue", "Thing: Example")
        self.assertEqual(
            self.colored.traceback(example, traceback),
            indent(name + "\n" + traceback, 4 * " "),
        )


class TestFormatter(TestCase, PatchMixin):
    def setUp(self):
        self.elapsed = 1.23456789
        self.result = mock.Mock()
        self.test = mock.Mock()
        self.exc_info = fake_exc_info()

        self.stream = StringIO()
        self.formatter = result.Formatter(self.stream)

    def test_it_writes_to_stderr_by_default(self):
        self.assertEqual(result.Formatter().stream, sys.stderr)

    def test_show_writes_and_flushes(self):
        self.stream.flush = mock.Mock()
        self.formatter.show("hello\n")
        self.assertEqual(self.stream.getvalue(), "hello\n")
        self.assertTrue(self.stream.flush.called)

    def test_result_summary(self):
        self.result.testsRun = 20
        self.result.errors = range(8)
        self.result.failures = range(2)

        self.assertEqual(
            self.formatter.result_summary(self.result),
            "20 examples, 8 errors, 2 failures\n",
        )

    def test_timing(self):
        self.assertEqual(
            self.formatter.timing(self.elapsed),
            "Finished in {:.6f} seconds.\n".format(self.elapsed),
        )

    def test_error(self):
        self.assertEqual(self.formatter.error(self.test, self.exc_info), "E")

    def test_failure(self):
        self.assertEqual(self.formatter.failure(self.test, self.exc_info), "F")

    def test_success(self):
        self.assertEqual(self.formatter.success(self.test), ".")

    def test_traceback(self):
        example = mock.MagicMock()
        example.__str__.return_value = "Example"
        traceback = "The\nTraceback\n"

        self.assertEqual(
            self.formatter.traceback(example, traceback),
            "\n".join([str(example), traceback])
        )


class TestVerboseFormatter(TestCase, PatchMixin):
    def setUp(self):
        self.exc_info = mock.Mock()
        self.formatter = mock.Mock()
        self.result = mock.Mock()
        self.test = mock.Mock()
        self.verbose = result.Verbose(self.formatter)

    def test_it_delegates_to_the_formatter(self):
        self.assertEqual(self.verbose.foo, self.formatter.foo)

    def test_finished(self):
        self.verbose.finished()
        self.formatter.show.assert_called_once_with("\n")

    def test_error(self):
        self.verbose.maybe_show_group = mock.Mock()
        self.assertEqual(
            self.verbose.error(self.test, self.exc_info),
            "    {} - ERROR\n".format(self.test)
        )
        self.verbose.maybe_show_group.assert_called_once_with(self.test.group)

    def test_failure(self):
        self.verbose.maybe_show_group = mock.Mock()
        self.assertEqual(
            self.verbose.failure(self.test, self.exc_info),
            "    {} - FAIL\n".format(self.test)
        )
        self.verbose.maybe_show_group.assert_called_once_with(self.test.group)

    def test_success(self):
        self.verbose.maybe_show_group = mock.Mock()
        self.assertEqual(
            self.verbose.success(self.test), "    {}\n".format(self.test)
        )
        self.verbose.maybe_show_group.assert_called_once_with(self.test.group)

    def test_maybe_show_group(self):
        self.verbose.maybe_show_group(self.test.group)
        self.verbose.show.assert_called_once_with(str(self.test.group) + "\n")

        self.verbose.show.reset_mock()

        self.verbose.maybe_show_group(self.test.group)
        self.assertFalse(self.verbose.show.called)
