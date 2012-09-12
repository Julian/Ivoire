from __future__ import unicode_literals
from unittest import TestCase, TestResult, TestSuite
import collections
import contextlib

import ivoire
from ivoire.result import ExampleResult, Formatter


class _ShouldStop(Exception):
    pass


# TestCase requires the name of an existing method on creation in 2.X because 
# of the way the default implementation of .run() works. So make it shut up.
_MAKE_UNITTEST_SHUT_UP = "__init__"


class Example(TestCase):
    """
    An ``Example`` is the smallest unit in a specification.

    """

    def __init__(self, name, group):
        result = self.__result = ivoire.current_result

        if result is None:
            raise ValueError(
                "ivoire.current_result must be set to a TestResult before "
                "execution starts!"
            )

        super(Example, self).__init__(_MAKE_UNITTEST_SHUT_UP)
        self.__group = group
        self.__name = name

    def __enter__(self):
        self.__result.startTest(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.__result.addSuccess(self)
        elif exc_type == KeyboardInterrupt:
            raise
        elif exc_type == self.failureException:
            self.__result.addFailure(self, (exc_type, exc_value, traceback))
        else:
            self.__result.addError(self, (exc_type, exc_value, traceback))

        self.doCleanups()
        self.__result.stopTest(self)

        if self.__result.shouldStop:
            raise _ShouldStop
        return True

    def __hash__(self):
        return hash((self.__class__, self.group, self.__name))

    def __repr__(self):
        return "<{self.__class__.__name__}: {self}>".format(self=self)

    def __str__(self):
        return self.__name

    @property
    def group(self):
        return self.__group


class ExampleGroup(object):
    """
    ``ExampleGroup``s group together a number of ``Example``s.

    """

    def __init__(self, describes, Example=Example):
        self.Example = Example
        self.describes = describes
        self.examples = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type == _ShouldStop:
            return True

    def __iter__(self):
        return iter(self.examples)

    def __repr__(self):
        return "<{self.__class__.__name__} examples={self.examples}>".format(
            self=self
        )

    def __call__(self, name):
        """
        Construct and return a new ``Example``.

        """

        example = self.Example(name=name, group=self)
        self.add_example(example)
        return example

    def add_example(self, example):
        """
        Add an existing ``Example`` to this group.

        """

        self.examples.append(example)

    def countTestCases(self):
        return sum(example.countTestCases() for example in self)


describe = ExampleGroup
