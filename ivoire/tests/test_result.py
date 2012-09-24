from __future__ import unicode_literals
from unittest import TestCase

from ivoire import result
from ivoire.compat import indent
from ivoire.tests.util import PatchMixin, mock


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
