from __future__ import unicode_literals
from functools import wraps
from unittest import TestCase

import ivoire
from ivoire.standalone import Example, ExampleGroup, describe
from ivoire.tests.util import PatchMixin, mock


class TestDescribe(TestCase, PatchMixin):
    def test_describe(self):
        self.assertEqual(describe, ExampleGroup)

    def test_it_can_have_Example_specified(self):
        self.patchObject(ivoire, "current_result")
        OtherExample = mock.Mock()

        it = ExampleGroup(describe, Example=OtherExample)
        self.assertEqual(it.Example, OtherExample)


class TestDescribeTests(TestCase, PatchMixin):
    def setUp(self):
        self.result = self.patchObject(
            ivoire, "current_result", shouldStop=False
        )
        self.describes = ExampleGroup
        self.it = ExampleGroup(self.describes)

    def test_repr(self):
        self.assertEqual(
            repr(self.it),
            "<{0.__class__.__name__} examples={0.examples}>".format(self.it)
        )

    def test_it_sets_the_described_object(self):
        self.assertEqual(self.it.describes, self.describes)

    def test_it_raises_an_error_if_the_result_is_not_set(self):
        self.patchObject(ivoire, "current_result", None)
        with self.assertRaises(ValueError):
            ExampleGroup(self.describes)

    def test_it_starts_and_stops_a_test_run(self):
        with self.it:
            self.result.startTestRun.assert_called_once_with()
        self.result.stopTestRun.assert_called_once_with()

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
            exc = self.patch("ivoire.standalone.sys.exc_info").return_value

            with it("does a thing") as test:
                test.fail()

        self.result.assert_has_calls([
                mock.call.startTest(test),
                mock.call.addFailure(test, exc),
                mock.call.stopTest(test),
        ])

    def test_it_can_error(self):
        with self.it as it:
            exc = self.patch("ivoire.standalone.sys.exc_info").return_value

            with it("does a thing") as test:
                raise IndexError()

        self.result.assert_has_calls([
                mock.call.startTest(test),
                mock.call.addError(test, exc),
                mock.call.stopTest(test),
        ])

    def test_it_does_not_swallow_KeyboardInterrupts(self):
        with self.assertRaises(KeyboardInterrupt):
            with self.it as it:
                with it("does a thing") as test:
                    raise KeyboardInterrupt

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
