"""
Specification for the ``describe`` function.

The rest of the specification is written as a pyUnit test case (in the
``tests``) directory, since nested ``describe``s are a bit confusing.

"""

from ivoire.spec.util import ExampleWithPatch, mock
from ivoire.standalone import ExampleGroup, describe
import ivoire

with describe(describe, Example=ExampleWithPatch) as it:

    @it.before
    def before(test):
        test.describes = mock.Mock(__name__="DescribedThing")
        test.it = describe(test.describes)

    with it("returns the described object's name as its str") as test:
        test.assertEqual(str(test.it), test.it.describes.__name__)

    with it("shows its name and examples as its repr") as test:
        test.assertEqual(
            repr(test.it),
            f"<{test.it.__class__.__name__} examples={test.it.examples}>",
        )

    with it("sets the described object") as test:
        test.assertEqual(test.it.describes, test.describes)

    with it("passes along failureException to Examples") as test:
        test.it.failureException = mock.Mock()
        test.assertEqual(
            test.it("Example").failureException,
            test.it.failureException,
        )

    with it("leaves the default failureException alone") as test:
        test.assertIsNone(test.it.failureException)
        test.assertIsNotNone(test.it("Example").failureException)

    with it("yields examples when iterating") as test:
        example, another = mock.Mock(), mock.Mock()
        test.it.add_example(example)
        test.it.add_example(another)
        test.assertEqual(list(test.it), [example, another])

    with it("counts its examples") as test:
        test.assertEqual(test.it.countTestCases(), 0)
        test.it.add_example(mock.Mock(**{"countTestCases.return_value": 3}))
        test.assertEqual(test.it.countTestCases(), 3)

    with it("can have Example specified") as test:
        OtherExample = mock.Mock()
        group = describe(ExampleGroup, Example=OtherExample)
        test.assertEqual(group.Example, OtherExample)

    with it("raises a ValueError if the global result is not set") as test:
        test.patchObject(ivoire, "current_result", None)
        with test.assertRaises(ValueError):
            with test.it:
                pass


with describe(ExampleGroup, Example=ExampleWithPatch) as it:
    with it("is aliased to describe") as test:
        test.assertEqual(describe, ExampleGroup)
