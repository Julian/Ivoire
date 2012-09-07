import collections
import contextlib

from unittest import TestCase, TestResult, TestSuite


# TestCase requires the name of an existing method on itself on creation,
# because of the way it's default implementation of .run() works. So shut up.
_MAKE_UNITTEST_SHUT_UP = "__init__"


class Example(TestCase):
    def __init__(self, name):
        super(Example, self).__init__(_MAKE_UNITTEST_SHUT_UP)
        self.name = name

    def __hash__(self):
        return hash((self.__class__, self.name))

    def __repr__(self):
        return "<{self.__class__.__name__}: {self.name}>".format(self=self)

    def run(self, result):
        result.startTest(self)
        result.stopTest(self)


class ExampleGroup(object):

    TestResultClass = TestResult

    def __init__(self, describes):
        self.describes = describes
        self.examples = []
        self.result = self.TestResultClass()

    def __enter__(self):
        self.result.startTestRun()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.result.stopTestRun()

    def __iter__(self):
        return iter(self.examples)

    def __repr__(self):
        return "<{self.__class__.__name__} examples={self.examples}>".format(
            self=self
        )

    @contextlib.contextmanager
    def __call__(self, description):
        example = Example(description)
        self.examples.append(example)
        yield example
        example.run(self.result)


describe = ExampleGroup
