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

import ivoire
from ivoire.standalone import Example, ExampleGroup, describe
from ivoire.tests.util import PatchMixin, mock


class TestDescribeTests(TestCase, PatchMixin):
    def setUp(self):
        self.result = self.patchObject(
            ivoire, "current_result", shouldStop=False
        )
        self.describes = ExampleGroup
        self.it = ExampleGroup(self.describes)

    def test_it_adds_an_example(self):
        with self.it as it:
            with it("does a thing") as test:
                pass
        self.assertEqual(it.examples, [test])

    def test_iterating_yields_examples(self):
        with self.it as it:
            with it("does a thing") as test:
                pass
        self.assertEqual(list(it), it.examples)

    def test_counts_its_examples(self):
        with self.it as it:
            pass

        self.assertEqual(it.countTestCases(), 0)
        it.add_example(mock.Mock(**{"countTestCases.return_value" : 3}))
        self.assertEqual(it.countTestCases(), 3)

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


class TestExample(TestCase, PatchMixin):
    def setUp(self):
        self.result = self.patchObject(
            ivoire, "current_result", shouldStop=False
        )
        self.name = "does a thing"
        self.group = mock.Mock()
        self.example = Example(self.name, self.group)

    def test_str(self):
        self.assertEqual(str(self.example), self.name)

    def test_repr(self):
        self.assertEqual(
            repr(self.example),
            "<{0.__class__.__name__}: {0}>".format(self.example)
        )

    def test_it_raises_an_error_if_the_result_is_not_set(self):
        self.patchObject(ivoire, "current_result", None)
        with self.assertRaises(ValueError):
            Example(self.name, self.group)

    def test_it_knows_its_group(self):
        self.assertEqual(self.example.group, self.group)

    def test_group_is_prevented_from_accidental_setting(self):
        with self.assertRaises(AttributeError):
            self.example.group = 12

    def test_same_name_and_group_has_the_same_hash(self):
        same = Example(self.name, self.group)
        self.assertEqual(hash(self.example), hash(same))

    def test_different_name_or_group_has_a_different_hash(self):
        other = Example("does a different thing", self.group)
        another = Example(str(self.example), mock.Mock())

        self.assertNotEqual(hash(self.example), hash(other))
        self.assertNotEqual(hash(self.example), hash(another))
