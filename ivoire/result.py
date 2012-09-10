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
        output = self.formatter.error(test, exc_info)
        self.formatter.show(output)

    def addFailure(self, test, exc_info):
        super(ExampleResult, self).addFailure(test, exc_info)
        output = self.formatter.failure(test, exc_info)
        self.formatter.show(output)

    def addSuccess(self, test):
        super(ExampleResult, self).addSuccess(test)
        output = self.formatter.success(test)
        self.formatter.show(output)

    def stopTestRun(self):
        super(ExampleResult, self).stopTestRun()
        self.elapsed = time.time() - self._start
        self.formatter.show(self.formatter.timing(self.elapsed))
        self.formatter.show(self.formatter.result(self))


class Colored(object):
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

    def result(self, result):
        output = self._formatter.result(result)

        if result.wasSuccessful():
            return self.color("green", output)
        return self.color("red", output)


class Formatter(object):
    def __init__(self, stream=sys.stderr):
        self.stream = stream

    def show(self, text):
        """
        Write the text to the stream and flush immediately.

        """

        self.stream.write(text)
        self.stream.flush()

    def result(self, result):
        return "\n{} examples, {} errors, {} failures\n".format(
            result.testsRun, len(result.errors), len(result.failures),
        )

    def timing(self, elapsed):
        return "\n\nFinished in {} seconds.\n".format(elapsed)

    def error(self, test, exc_info):
        return "E"

    def failure(self, test, exc_info):
        return "F"

    def success(self, test):
        return "."
