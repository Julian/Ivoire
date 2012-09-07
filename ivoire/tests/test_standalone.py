from functools import wraps
from unittest import TestCase, TestResult, TestSuite

from ivoire.standalone import Example, ExampleGroup, describe
from ivoire.tests.util import PatchMixin, mock


class TestExampleGroup(TestCase, PatchMixin):
    def setUp(self):
        self.describes = ExampleGroup
        self.it = ExampleGroup(self.describes)

    def test_repr(self):
        self.assertEqual(
            repr(self.it),
            "<{0.__class__.__name__} examples={0.examples}>".format(self.it)
        )

    def test_it_sets_the_described_object(self):
        self.assertEqual(self.it.describes, self.describes)

    def test_it_starts_and_stops_a_test_run(self):
        result = self.patchObject(self.it, "result")

        with self.it:
            pass

        self.assertEqual(
            result.mock_calls,
            [mock.call.startTestRun(), mock.call.stopTestRun()],
        )

    def test_describe(self):
        self.assertEqual(describe, ExampleGroup)


class TestDescribeTests(TestCase, PatchMixin):
    def setUp(self):
        with describe(describe) as it:
            pass
        self.it = it

    def test_it_adds_an_example(self):
        with self.it("does a thing") as test:
            pass
        self.assertEqual(self.it.examples, [test])

    def test_iterating_yields_examples(self):
        with self.it("does a thing") as test:
            pass
        self.assertEqual(list(self.it), self.it.examples)

    def test_it_passes_along_its_test_result_to_each_test(self):
        result = self.patchObject(self.it, "result")

        with self.it("does a thing") as test:
            run = self.patchObject(test, "run")
        run.assert_called_once_with(result)

        with self.it("does another thing") as test:
            run = self.patchObject(test, "run")
        run.assert_called_once_with(result)


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
