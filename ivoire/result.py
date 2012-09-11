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
        stats = self.formatter.statistics(elapsed=self.elapsed, result=self)
        self.formatter.show(stats)


class FormatterMixin(object):
    """
    Provide some higher-level formatting using the child's building blocks.

    """

    def statistics(self, elapsed, result):
        return "\n".join((self.timing(elapsed), self.result_summary(result)))


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
        return "{} examples, {} errors, {} failures\n".format(
            result.testsRun, len(result.errors), len(result.failures),
        )

    def timing(self, elapsed):
        return "\n\nFinished in {:.6f} seconds.\n".format(elapsed)

    def error(self, test, exc_info):
        return "E"

    def failure(self, test, exc_info):
        return "F"

    def success(self, test):
        return "."
