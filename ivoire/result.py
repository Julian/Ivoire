from __future__ import unicode_literals
from unittest import TestResult
import sys
import time

from ivoire.compat import indent


class ExampleResult(TestResult):
    """
    Track the outcomes of example runs.

    """

    def __init__(self, formatter):
        super(ExampleResult, self).__init__()
        self.formatter = formatter

    def startTestRun(self):
        super(ExampleResult, self).startTestRun()
        self._start = time.time()

    def addError(self, example, exc_info):
        super(ExampleResult, self).addError(example, exc_info)
        self.formatter.show(self.formatter.error(example, exc_info))

    def addFailure(self, example, exc_info):
        super(ExampleResult, self).addFailure(example, exc_info)
        self.formatter.show(self.formatter.failure(example, exc_info))

    def addSuccess(self, example):
        super(ExampleResult, self).addSuccess(example)
        self.formatter.show(self.formatter.success(example))

    def addSkip(self, example, reason):
        super(ExampleResult, self).addSkip(example, reason)
        self.formatter.show(self.formatter.skip(example, reason))

    def stopTestRun(self):
        super(ExampleResult, self).stopTestRun()
        self.elapsed = time.time() - self._start

        self.formatter.finished()
        self.formatter.show(self.formatter.errors(self.errors))
        self.formatter.show(self.formatter.failures(self.failures))
        self.formatter.show(
            self.formatter.statistics(elapsed=self.elapsed, result=self)
        )


class FormatterMixin(object):
    """
    Provide some higher-level formatting using the child's building blocks.

    """

    def finished(self):
        """
        The run has finished.

        """

        self.show("\n\n")

    def statistics(self, elapsed, result):
        """
        Return output for the combined time and result summary statistics.

        """

        return "\n".join((self.timing(elapsed), self.result_summary(result)))

    def errors(self, errors):
        if not errors:
            return ""

        tracebacks = (self.traceback(error, tb) for error, tb in errors)
        return "\n".join(["Errors:\n", "\n".join(tracebacks), ""])

    def failures(self, failures):
        if not failures:
            return ""

        tracebacks = (self.traceback(fail, tb) for fail, tb in failures)
        return "\n".join(["Failures:\n", "\n".join(tracebacks), ""])


class Colored(FormatterMixin):
    """
    Wrap a formatter to show colored output.

    """

    ANSI = {
        "reset" : "\x1b[0m",
        "black" : "\x1b[30m",
        "red" : "\x1b[31m",
        "green" : "\x1b[32m",
        "yellow" : "\x1b[33m",
        "blue" : "\x1b[34m",
        "magenta" : "\x1b[35m",
        "cyan" : "\x1b[36m",
        "gray" : "\x1b[37m",
    }

    def __init__(self, formatter):
        self._formatter = formatter

    def __getattr__(self, attr):
        """
        Delegate to the wrapped formatter.

        """

        return getattr(self._formatter, attr)

    def color(self, color, text):
        """
        Color some text in the given ANSI color.

        """

        return "{escape}{text}{reset}".format(
            escape=self.ANSI[color], text=text, reset=self.ANSI["reset"],
        )

    def error(self, example, exc_info):
        return self.color("red", self._formatter.error(example, exc_info))

    def failure(self, example, exc_info):
        return self.color("red", self._formatter.failure(example, exc_info))

    def success(self, example):
        return self.color("green", self._formatter.success(example))

    def traceback(self, example, traceback):
        name = str(example.group) + ": " + str(example)
        colored = "\n".join([self.color("blue", name), traceback])
        return indent(colored, 4 * " ")

    def result_summary(self, result):
        output = self._formatter.result_summary(result)

        if result.wasSuccessful():
            return self.color("green", output)
        return self.color("red", output)


class DotsFormatter(FormatterMixin):
    def __init__(self, stream=sys.stderr):
        self.stream = stream

    def show(self, text):
        """
        Write the text to the stream and flush immediately.

        """

        self.stream.write(text)
        self.stream.flush()

    def result_summary(self, result):
        """
        Return a summary of the results.

        """

        return "{} examples, {} errors, {} failures\n".format(
            result.testsRun, len(result.errors), len(result.failures),
        )

    def timing(self, elapsed):
        """
        Return output on the time taken on the examples run.

        """

        return "Finished in {:.6f} seconds.\n".format(elapsed)

    def error(self, example, exc_info):
        """
        An error was encountered.

        """

        return "E"

    def failure(self, example, exc_info):
        """
        A failure was encountered.

        """

        return "F"

    def skip(self, example, reason):
        """
        A skip was encountered.

        """

        return "S"

    def success(self, example):
        """
        A success was encountered.

        """

        return "."

    def traceback(self, example, traceback):
        """
        Format an example and its traceback.

        """

        return "\n".join((str(example), traceback))


class Verbose(FormatterMixin):
    """
    Show verbose output (including example and group descriptions.

    """

    _last_group = None

    def __init__(self, formatter):
        self._formatter = formatter

    def __getattr__(self, attr):
        return getattr(self._formatter, attr)

    def finished(self):
        self.show("\n")

    def error(self, example, exc_info):
        self.maybe_show_group(example.group)
        return indent(str(example), 4 * " ") + " - ERROR\n"

    def failure(self, example, exc_info):
        self.maybe_show_group(example.group)
        return indent(str(example), 4 * " ") + " - FAIL\n"

    def success(self, example):
        self.maybe_show_group(example.group)
        return indent(str(example), 4 * " ") + "\n"

    def maybe_show_group(self, group):
        """
        Show the given example group if it is different than the last seen.

        """

        if group != self._last_group:
            self.show(str(group) + "\n")
        self._last_group = group
