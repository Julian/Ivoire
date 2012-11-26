from __future__ import unicode_literals
from unittest import SkipTest, TestCase, TestResult
import sys

import ivoire


class _ShouldStop(Exception):
    pass


# TestCase requires the name of an existing method on creation in 2.X because 
# of the way the default implementation of .run() works. So make it shut up.
_MAKE_UNITTEST_SHUT_UP = "__init__"


class Example(TestCase):
    """
    An ``Example`` is the smallest unit in a specification.

    """

    def __init__(self, name, group, before=None, after=None):
        super(Example, self).__init__(_MAKE_UNITTEST_SHUT_UP)
        self.__after = after
        self.__before = before
        self.__group = group
        self.__name = name
        self.__result = group.result

    def __enter__(self):
        """
        Run the example.

        """

        self.__result.startTest(self)

        if self.__before is not None:
            try:
                self.__before(self)
            except Exception:
                self.__result.addError(self, sys.exc_info())
                self.__result.stopTest(self)
                raise _ShouldStop

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Finish running the example, logging any raised exceptions as results.

        """
        if exc_type is None:
            self.__result.addSuccess(self)
        elif exc_type == KeyboardInterrupt:
            return False
        elif exc_type == SkipTest:
            self.__result.addSkip(self, str(exc_value))
        elif exc_type == self.failureException:
            self.__result.addFailure(self, (exc_type, exc_value, traceback))
        else:
            self.__result.addError(self, (exc_type, exc_value, traceback))

        if self.__after is not None:
            self.__after(self)

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

    def skip_if(self, condition, reason):
        """
        Skip the example if the condition is set, with the provided reason.

        """

        if condition:
            raise SkipTest(reason)


class ExampleGroup(object):
    """
    ``ExampleGroup``s group together a number of ``Example``s.

    """

    _before = _after = None
    failureException = None
    result = None

    def __init__(self, describes, Example=Example):
        self.Example = Example
        self.describes = describes
        self.examples = []

    def __enter__(self):
        """
        Begin running the group.

        """

        self.result = _get_result()

        enterGroup = getattr(self.result, "enterGroup", None)
        if enterGroup is not None:
            enterGroup(self)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        exitGroup = getattr(self.result, "exitGroup", None)
        if exitGroup is not None:
            exitGroup(self)

        if exc_type == _ShouldStop:
            return True

    def __iter__(self):
        return iter(self.examples)

    def __repr__(self):
        return "<{self.__class__.__name__} examples={self.examples}>".format(
            self=self
        )

    def __str__(self):
        return self.describes.__name__

    def __call__(self, name):
        """
        Construct and return a new ``Example``.

        """

        example = self.Example(
            name=name, group=self, before=self._before, after=self._after,
        )

        if self.failureException is not None:
            example.failureException = self.failureException

        self.add_example(example)
        return example

    def add_example(self, example):
        """
        Add an existing ``Example`` to this group.

        """

        self.examples.append(example)

    def before(self, fn):
        """
        Run the given function before each example is run.

        Note: In standalone mode, it's not possible to skip a context block,
        so if a ``before`` function errors, the exception is propagated all the
        way up to the ``ExampleGroup`` (meaning the rest of the examples *will
        not run at all*, nor will they show up in the result output).

        """

        self._before = fn

    def after(self, fn):
        """
        Run the given function after each example is run.

        """

        self._after = fn

    def countTestCases(self):
        return sum(example.countTestCases() for example in self)


describe = ExampleGroup


def _get_result():
    """
    Find the global result object.

    """

    result = ivoire.current_result
    if result is None:
        raise ValueError(
            "ivoire.current_result must be set to a TestResult before "
            "execution starts!"
        )
    return result
