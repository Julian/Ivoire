from __future__ import unicode_literals
from unittest import TestCase, TestResult, TestSuite
import collections
import contextlib
import sys

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
        super(Example, self).__init__(_MAKE_UNITTEST_SHUT_UP)
        self.__group = group
        self.__name = name

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
        result = self._result = ivoire.current_result

        if result is None:
            raise ValueError(
                "ivoire.current_result must be set to a TestResult before "
                "execution starts!"
            )

        self.Example = Example
        self.describes = describes
        self.examples = []

    def __enter__(self):
        self._result.startTestRun()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type == _ShouldStop:
            return True
        self._result.stopTestRun()

    def __iter__(self):
        return iter(self.examples)

    def __repr__(self):
        return "<{self.__class__.__name__} examples={self.examples}>".format(
            self=self
        )

    @contextlib.contextmanager
    def __call__(self, name):
        """
        Construct and return a new ``Example``.

        """

        example = self.Example(name, self)
        self.add_example(example)
        self._result.startTest(example)
        try:
            yield example
        except KeyboardInterrupt:
            raise
        except example.failureException:
            self._result.addFailure(example, sys.exc_info())
        except:
            self._result.addError(example, sys.exc_info())
        else:
            self._result.addSuccess(example)
        finally:
            example.doCleanups()
            self._result.stopTest(example)

            if self._result.shouldStop:
                raise _ShouldStop

    def add_example(self, example):
        """
        Add an existing ``Example`` to this group.

        """

        self.examples.append(example)

    def countTestCases(self):
        return sum(example.countTestCases() for example in self)


describe = ExampleGroup
