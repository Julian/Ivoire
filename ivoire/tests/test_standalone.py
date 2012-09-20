"""
Test the standalone running of Ivoire examples.

A **warning** about testing in this module: Testing Ivoire Examples means
testing a thing that is swallowing (and recording) *all* exceptions. Make sure
all of your assertions are outside of example blocks so that they are handled
by the surrounding test case.

"""

from __future__ import unicode_literals
from unittest import TestCase
import sys

from ivoire.standalone import describe
from ivoire.tests.util import PatchMixin, mock


class TestDescribeTests(TestCase, PatchMixin):
    def setUp(self):
        self.result = self.patch("ivoire.current_result", shouldStop=False)
        self.describes = describe
        self.it = describe(self.describes)

    def test_it_adds_an_example(self):
        with self.it as it:
            with it("does a thing") as test:
                pass
        self.assertEqual(it.examples, [test])

    def test_it_can_pass(self):
        with self.it as it:
            with it("does a thing") as test:
                pass

        self.result.assert_has_calls([
            mock.call.startTest(test),
            mock.call.addSuccess(test),
            mock.call.stopTest(test),
        ])


    def test_it_can_fail(self):
        with self.it as it:
            with it("does a thing") as test:
                try:
                    test.fail()
                except Exception:
                    exc_info = sys.exc_info()
                    raise

        self.result.assert_has_calls([
                mock.call.startTest(test),
                mock.call.addFailure(test, exc_info),
                mock.call.stopTest(test),
        ])

    def test_it_can_error(self):
        with self.it as it:
            with it("does a thing") as test:
                try:
                    raise IndexError
                except IndexError:
                    exc_info = sys.exc_info()
                    raise

        self.result.assert_has_calls([
                mock.call.startTest(test),
                mock.call.addError(test, exc_info),
                mock.call.stopTest(test),
        ])

    def test_it_does_not_swallow_KeyboardInterrupts(self):
        with self.assertRaises(KeyboardInterrupt):
            with self.it as it:
                with it("does a thing") as test:
                    raise KeyboardInterrupt

    def test_it_exits_the_group_if_begin_errors(self):
        self.ran_test = False

        with self.it as it:
            @it.before
            def before(test):
                raise RuntimeError("Buggy before.")

            example = it("should not be run")
            with example as test:
                self.ran_test = True

        self.assertEqual(self.result.mock_calls, [
            mock.call.startTest(example),
            mock.call.addError(example, mock.ANY),  # traceback object
            mock.call.stopTest(example),
        ])
        self.assertFalse(self.ran_test)

    def test_it_runs_befores(self):
        with self.it as it:
            @it.before
            def before(test):
                test.foo = 12

            with it("should have set foo") as test:
                foo = test.foo
        self.assertEqual(foo, 12)

    # XXX: There's a few more cases here that should be tested

    def test_it_runs_afters(self):
        self.foo = None

        with self.it as it:
            @it.after
            def after(test):
                self.foo = 12

            with it("should have set foo after") as test:
                foo = self.foo

        self.assertEqual(foo, None)
        self.assertEqual(self.foo, 12)

    def test_it_runs_cleanups(self):
        with self.it as it:
            with it("does a thing") as test:
                doCleanups = self.patchObject(test, "doCleanups")
        self.assertTrue(doCleanups.called)

    def test_it_respects_shouldStop(self):
        with self.it as it:
            with it("does a thing") as test:
                self.result.shouldStop = True
            self.fail("should have stopped already!")  # pragma: no cover

    def test_it_can_skip(self):
        with self.it as it:
            with it("should skip this test") as test:
                test.skip_if(False, reason="A bad one")
                test.skip_if(True, reason="A good one")
                test.fail("Should have skipped!")

        self.assertEqual(self.result.method_calls, [
            mock.call.startTest(test),
            mock.call.addSkip(test, "A good one"),
            mock.call.stopTest(test),
        ])
