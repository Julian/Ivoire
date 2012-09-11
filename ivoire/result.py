from __future__ import unicode_literals
from textwrap import dedent
from unittest import TestResult
import sys
import time


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

    def addError(self, test, exc_info):
        super(ExampleResult, self).addError(test, exc_info)
        self.formatter.show(self.formatter.error(test, exc_info))

    def addFailure(self, test, exc_info):
        super(ExampleResult, self).addFailure(test, exc_info)
        self.formatter.show(self.formatter.failure(test, exc_info))

    def addSuccess(self, test):
        super(ExampleResult, self).addSuccess(test)
        self.formatter.show(self.formatter.success(test))

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

    def error(self, test, exc_info):
        return self.color("red", self._formatter.error(test, exc_info))

    def failure(self, test, exc_info):
        return self.color("red", self._formatter.failure(test, exc_info))

    def success(self, test):
        return self.color("green", self._formatter.success(test))

    def traceback(self, test, traceback):
        return "\n".join([self.color("blue", str(test)), traceback])

    def result_summary(self, result):
        output = self._formatter.result_summary(result)

        if result.wasSuccessful():
            return self.color("green", output)
        return self.color("red", output)


class Formatter(FormatterMixin):
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

    def error(self, test, exc_info):
        """
        An error was encountered.

        """

        return "E"

    def failure(self, test, exc_info):
        """
        A failure was encountered.

        """

        return "F"

    def success(self, test):
        """
        A success was encountered.

        """

        return "."

    def traceback(self, test, traceback):
        """
        Format an example and its traceback.

        """

        return "\n".join((str(test), traceback))
