import collections
import contextlib

from unittest import TestCase


try:
    # In Python2's unittest, there is no default implementation of runTest,
    # which we need to be able to instante TestCases just to use their asserts
    TestCase()
except ValueError:
    class TestCase(TestCase):
        def runTest(self):
            pass


class ExampleGroup(object):
    def __init__(self, subject):
        self.succeeded = collections.OrderedDict()
        self.subject = subject

    @contextlib.contextmanager
    def __call__(self, description):
        test_case = TestCase()
        self.succeeded[description] = None
        try:
            yield test_case
        except Exception:
            succeeded = False
        else:
            succeeded = True
        finally:
            self.succeeded[description] = succeeded

    add_example = __call__

    @classmethod
    @contextlib.contextmanager
    def describe(cls, subject):
        yield cls(subject)

    @property
    def examples(self):
        return list(self.succeeded)


describe = ExampleGroup.describe
