from __future__ import unicode_literals
from io import StringIO
from textwrap import dedent
from unittest import TestCase
import sys

from ivoire import result
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

    def test_show_statistics(self):
        self.result.startTestRun()
        self.result.stopTestRun()

        self.formatter.timing.assert_called_once_with(self.result.elapsed)
        self.assertShown(self.formatter.timing.return_value)

        self.formatter.result.assert_called_once_with(self.result)
        self.assertShown(self.formatter.result.return_value)


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
        self.formatter.result.return_value = "results"
        self.assertEqual(
            self.colored.result(self.result),
            self.colored.color("green", "results"),
        )

    def test_it_colors_result_red_when_unsuccessful(self):
        self.result.wasSuccessful.return_value = False
        self.formatter.result.return_value = "results"
        self.assertEqual(
            self.colored.result(self.result),
            self.colored.color("red", "results"),
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

    def test_result(self):
        self.result.testsRun = 20
        self.result.errors = range(8)
        self.result.failures = range(2)

        self.assertEqual(
            self.formatter.result(self.result),
            "\n20 examples, 8 errors, 2 failures\n",
        )

    def test_timing(self):
        self.assertEqual(
            self.formatter.timing(self.elapsed),
            "\n\nFinished in {} seconds.\n".format(self.elapsed),
        )

    def test_error(self):
        self.assertEqual(self.formatter.error(self.test, self.exc_info), "E")

    def test_failure(self):
        self.assertEqual(self.formatter.failure(self.test, self.exc_info), "F")

    def test_success(self):
        self.assertEqual(self.formatter.success(self.test), ".")
