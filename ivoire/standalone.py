from __future__ import unicode_literals
from unittest import TestCase, TestResult, TestSuite
import collections
import contextlib
import sys

from ivoire.result import IvoireResult


class _ShouldStop(Exception):
    pass


# TestCase requires the name of an existing method on itself on creation,
# because of the way it's default implementation of .run() works. So shut up.
_MAKE_UNITTEST_SHUT_UP = "__init__"


class Example(TestCase):
    """
    An ``Example`` is the smallest unit in a specification.

    """

    def __init__(self, name):
        super(Example, self).__init__(_MAKE_UNITTEST_SHUT_UP)
        self.__name = name

    def __hash__(self):
        return hash((self.__class__, self.__name))

    def __repr__(self):
        return "<{self.__class__.__name__}: {self}>".format(self=self)

    def __str__(self):
        return self.__name


class ExampleGroup(object):
    """
    ``ExampleGroup``s group together a number of ``Example``s.

    """

    DefaultResult = IvoireResult

    def __init__(self, describes, failfast=False, Example=Example):
        self.Example = Example
        self.describes = describes
        self.examples = []

        self.result = self.DefaultResult()
        self.result.failfast = failfast

    def __enter__(self):
        self.result.startTestRun()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type == _ShouldStop:
            return True
        self.result.stopTestRun()

    def __iter__(self):
        return iter(self.examples)

    def __repr__(self):
        return "<{self.__class__.__name__} examples={self.examples}>".format(
            self=self
        )

    @contextlib.contextmanager
    def __call__(self, description):
        """
        Construct and return a new ``Example``.

        """

        example = self.Example(description)
        self.add_example(example)
        self.result.startTest(example)
        try:
            yield example
        except KeyboardInterrupt:
            raise
        except example.failureException:
            self.result.addFailure(example, sys.exc_info())
        except:
            self.result.addError(example, sys.exc_info())
        else:
            self.result.addSuccess(example)
        finally:
            example.doCleanups()
            self.result.stopTest(example)

            if self.result.shouldStop:
                raise _ShouldStop

    def add_example(self, example):
        """
        Add an existing ``Example`` to this group.

        """

        self.examples.append(example)

    def countTestCases(self):
        return sum(example.countTestCases() for example in self)


describe = ExampleGroup
