from __future__ import unicode_literals
from unittest import TestResult
import sys
import time


def green(s): return s.join(["\x1b[32m", "\x1b[0m"])
def red(s): return s.join(["\x1b[31m", "\x1b[0m"])


class IvoireResult(TestResult):
    """
    The basic Ivoire test result object.

    """

    _NO_COLOR = {"error" : "E", "failure" : "F", "success" : "."}
    _COLOR = {
        "error" : red("E"), "failure" : red("F"), "success" : green("."),
    }

    def __init__(self, stream=sys.stderr, colored=True):
        super(IvoireResult, self).__init__()
        self.colored = colored
        self.stream = stream

    def startTestRun(self):
        super(IvoireResult, self).startTestRun()
        self._start_time = time.time()

    def addError(self, test, exc_info):
        super(IvoireResult, self).addError(test, exc_info)
        self.stream.write(self.output["error"])
        self.stream.flush()

    def addFailure(self, test, exc_info):
        super(IvoireResult, self).addFailure(test, exc_info)
        self.stream.write(self.output["failure"])
        self.stream.flush()

    def addSuccess(self, test):
        super(IvoireResult, self).addSuccess(test)
        self.stream.write(self.output["success"])
        self.stream.flush()

    def stopTestRun(self):
        self.stream.write(
            "\n\nFinished in {:.6f} seconds.\n".format(
                time.time() - self._start_time,
            )
        )
        self.stream.write(self._statistics())
        self.stream.flush()

    @property
    def colored(self):
        return self.output == self._COLOR

    @colored.setter
    def colored(self, colored):
        self.output = self._COLOR if colored else self._NO_COLOR

    def _statistics(self):
        run = self.testsRun
        errors, failures = len(self.errors), len(self.failures)
        pluralize = ("s" if i != 1 else "" for i in (run, errors, failures))
        output = "{0} example{3}, {1} error{4}, {2} failure{5}".format(
            run, errors, failures, *pluralize
        )

        if self.wasSuccessful():
            return green(output).join("\n\n")
        return red(output).join("\n\n")
