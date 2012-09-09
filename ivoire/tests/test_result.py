from __future__ import unicode_literals
from io import FileIO, StringIO
from unittest import TestCase
import sys

from ivoire.result import IvoireResult
from ivoire.tests.util import PatchMixin, mock


class TestIvoireResult(TestCase, PatchMixin):
    def test_writes_to_stderr_by_default(self):
        self.assertEqual(IvoireResult().stream, sys.stderr)

    def test_default_is_color(self):
        result = IvoireResult()
        self.assertTrue(result.colored)


class TestIvoireResultOutput(TestCase, PatchMixin):
    def setUp(self):
        self.stream = StringIO()
        self.flush = self.patchObject(self.stream, "flush")
        self.result = IvoireResult(self.stream)
        self.test = mock.Mock()

        try:
            raise Exception
        except Exception:
            self.exc_info = sys.exc_info()

    def test_colored_output(self):
        self.result.colored = True
        self.result.addSuccess(self.test)
        self.result.addError(self.test, self.exc_info)
        self.result.addFailure(self.test, self.exc_info)
        self.assertEqual(
            self.stream.getvalue(),
            "\x1b[32m.\x1b[0m\x1b[31mE\x1b[0m\x1b[31mF\x1b[0m",
        )

    def test_uncolored_output(self):
        self.result.colored = False
        self.result.addSuccess(self.test)
        self.result.addError(self.test, self.exc_info)
        self.result.addFailure(self.test, self.exc_info)
        self.assertEqual(self.stream.getvalue(), ".EF")
