from __future__ import unicode_literals
from unittest import TestResult
import sys


def green(s): return s.join(["\x1b[32m", "\x1b[0m"])
def red(s): return s.join(["\x1b[31m", "\x1b[0m"])


class IvoireResult(TestResult):

    _NO_COLOR = {"error" : "E", "failure" : "F", "success" : "."}
    _COLOR = {
        "error" : red("E"), "failure" : red("F"), "success" : green("."),
    }

    def __init__(self, stream=sys.stderr, colored=True):
        super(IvoireResult, self).__init__()
        self.colored = colored
        self.stream = stream

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

    @property
    def colored(self):
        return self.output == self._COLOR

    @colored.setter
    def colored(self, colored):
        self.output = self._COLOR if colored else self._NO_COLOR
