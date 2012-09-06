from functools import wraps
from unittest import TestCase

from ivoire import standalone as ivoire
from ivoire.tests.util import PatchMixin


FAKE_MODULE, FAKE_PATH = "a_module", "a/path"


class TestDescribe(TestCase, PatchMixin):
    def test_subject(self):
        with ivoire.describe(ivoire.describe) as it:
            self.assertEqual(it.subject, ivoire.describe)

    def test_calling_adds_and_example(self):
        with ivoire.describe(ivoire.describe) as it:
            self.assertEqual(it.add_example, it.__call__)

    def test_adds_an_example(self):
        with ivoire.describe(ivoire.describe) as it:
            with it("adds an example") as test:
                self.assertEqual(it.examples, ["adds an example"])

    def test_can_pass_a_test(self):
        with ivoire.describe(ivoire.describe) as it:
            with it("can pass") as test:
                self.assertEqual(it.succeeded, {"can pass" : None})
        self.assertEqual(it.succeeded, {"can pass" : True})

    def test_can_fail_a_test(self):
        with ivoire.describe(ivoire.describe) as it:
            with it("can fail") as test:
                self.assertEqual(it.succeeded, {"can fail" : None})
                test.fail()
        self.assertEqual(it.succeeded, {"can fail" : False})
