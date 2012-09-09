from functools import wraps
from unittest import TestCase, TestResult, TestSuite

from ivoire.standalone import Example, ExampleGroup, describe
from ivoire.tests.util import PatchMixin, mock


class TestDescribeTests(TestCase, PatchMixin):
    def test_describe(self):
        self.assertEqual(describe, ExampleGroup)

    def test_repr(self):
        it = ExampleGroup(describe)
        self.assertEqual(
            repr(it),
            "<{0.__class__.__name__} examples={0.examples}>".format(it)
        )

    def test_it_sets_the_described_object(self):
        it = ExampleGroup(describe)
        self.assertEqual(it.describes, describe)

    def test_it_starts_and_stops_a_test_run(self):
        it = ExampleGroup(describe)
        result = self.patchObject(it, "result")
        with it:
            self.assertEqual(result.mock_calls, [mock.call.startTestRun()])
        result.stopTestRun.assert_called_once_with()

    def test_it_adds_an_example(self):
        with describe(describe) as it:
            with it("does a thing") as test:
                pass
        self.assertEqual(it.examples, [test])

    def test_iterating_yields_examples(self):
        with describe(describe) as it:
            with it("does a thing") as test:
                pass
        self.assertEqual(list(it), it.examples)

    def test_counts_its_examples(self):
        with describe(describe) as it:
            pass

        self.assertEqual(it.countTestCases(), 0)
        it.add_example(mock.Mock(**{"countTestCases.return_value" : 3}))
        self.assertEqual(it.countTestCases(), 3)

    def test_it_can_pass(self):
        with describe(describe) as it:
            result = self.patchObject(it, "result", shouldStop=False)

            with it("does a thing") as test:
                pass

            self.assertEqual(result.mock_calls, [
                mock.call.startTest(test),
                mock.call.addSuccess(test),
                mock.call.stopTest(test),
            ])


    def test_it_can_fail(self):
        with describe(describe) as it:
            result = self.patchObject(it, "result", shouldStop=False)
            exc = self.patch("ivoire.standalone.sys.exc_info").return_value

            with it("does a thing") as test:
                test.fail()

            self.assertEqual(
                result.mock_calls, [
                    mock.call.startTest(test),
                    mock.call.addFailure(test, exc),
                    mock.call.stopTest(test),
                ]
            )

    def test_it_can_error(self):
        with describe(describe) as it:
            result = self.patchObject(it, "result", shouldStop=False)
            exc = self.patch("ivoire.standalone.sys.exc_info").return_value

            with it("does a thing") as test:
                raise IndexError()

            self.assertEqual(
                result.mock_calls, [
                    mock.call.startTest(test),
                    mock.call.addError(test, exc),
                    mock.call.stopTest(test),
                ]
            )

    def test_it_does_not_swallow_KeyboardInterrupts(self):
        with self.assertRaises(KeyboardInterrupt):
            with describe(describe) as it:
                with it("does a thing") as test:
                    raise KeyboardInterrupt

    def test_it_runs_cleanups(self):
        with describe(describe) as it:
            with it("does a thing") as test:
                doCleanups = self.patchObject(test, "doCleanups")
            self.assertTrue(doCleanups.called)

    def test_it_can_have_Example_specified(self):
        class OtherExample(Example):
            pass

        with describe(describe, Example=OtherExample) as it:
            self.assertEqual(it.Example, OtherExample)

    def test_it_respects_fail_fast(self):
        with describe(describe, failfast=True) as it:
            with it("does a thing") as test:
                test.fail()
            self.fail("describe should have stopped after the first fail.")


class TestExample(TestCase, PatchMixin):
    def setUp(self):
        self.name = "does a thing"
        self.example = Example(self.name)

    def test_it_knows_its_name(self):
        self.assertEqual(str(self.example), self.name)

    def test_repr(self):
        self.assertEqual(
            repr(self.example),
            "<{0.__class__.__name__}: {0}>".format(self.example)
        )

    def test_same_name_has_the_same_hash(self):
        same = Example(self.name)
        self.assertEqual(hash(self.example), hash(same))

    def test_different_name_has_a_different_hash(self):
        other = Example("does a different thing")
        self.assertNotEqual(hash(self.example), hash(other))
