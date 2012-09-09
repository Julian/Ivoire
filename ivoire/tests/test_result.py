from __future__ import unicode_literals
from io import FileIO, StringIO
from textwrap import dedent
from unittest import TestCase
import sys

from ivoire import result
from ivoire.tests.util import PatchMixin, mock


class TestIvoireResult(TestCase, PatchMixin):
    def test_writes_to_stderr_by_default(self):
        self.assertEqual(result.IvoireResult().stream, sys.stderr)

    def test_default_is_color(self):
        self.assertTrue(result.IvoireResult().colored)


class TestIvoireResultOutput(TestCase, PatchMixin):
    def setUp(self):
        self.stream = StringIO()
        self.flush = self.patchObject(self.stream, "flush")
        self.result = result.IvoireResult(self.stream)
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

    def test_shows_uncolored_statistics(self):
        self.result.colored = False
        start, end = .123456, 1.123456
        self.patchObject(result.time, "time", side_effect=[start, end])
        self.result.startTestRun()
        self.result.testsRun = 4
        self.result.stopTestRun()
        self.assertEqual(
            self.stream.getvalue(), dedent("""

            Finished in {:.6f} seconds.

            4 examples, 0 errors, 0 failures
            """.format(end - start)
            )
        )

    def test_shows_colored_success_statistics(self):
        self.result.colored = True
        start, end = .123456, 1.123456
        self.patchObject(result.time, "time", side_effect=[start, end])
        self.result.startTestRun()
        self.result.testsRun = 4
        self.result.stopTestRun()
        self.assertEqual(
            self.stream.getvalue(), dedent("""

            Finished in {:.6f} seconds.

            \x1b[32m4 examples, 0 errors, 0 failures\x1b[0m
            """.format(end - start)
            )
        )

    def test_shows_colored_failure_statistics(self):
        self.result.colored = True
        start, end = .123456, 1.123456
        self.patchObject(result.time, "time", side_effect=[start, end])
        self.result.startTestRun()
        self.result.testsRun = 4
        failures = self.result.failures = [("foo's name", "foo")]
        errors = self.result.errors = [
            ("bar's name", "bar"), ("baz's name", "baz")
        ]
        self.result.stopTestRun()
        self.assertEqual(
            self.stream.getvalue(), dedent("""

            Failures:

            foo

            Errors:

            bar

            baz

            Finished in {:.6f} seconds.

            \x1b[31m4 examples, 2 errors, 1 failure\x1b[0m
            """.format(end - start)
            )
        )
