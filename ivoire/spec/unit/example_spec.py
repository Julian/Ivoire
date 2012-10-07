from ivoire.standalone import Example, describe
from ivoire.spec.util import ExampleWithPatch, mock


with describe(Example, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.name = "the name of the Example"
        test.example_group = mock.Mock()
        test.example = Example(test.name, test.example_group)

    with it("shows its name as its str") as test:
        test.assertEqual(str(test.example), test.name)

    with it("shows its class and name in its repr") as test:
        test.assertEqual(
            repr(test.example),
            "<{0.__class__.__name__}: {0}>".format(test.example),
        )

    with it("knows its group") as test:
        test.assertEqual(test.example.group, test.example_group)

    with it("prevents group from being accidentally set") as test:
        with test.assertRaises(AttributeError):
            test.example.group = 12

    with it("has the same hash for the same name and group") as test:
        same = Example(test.name, test.example_group)
        test.assertEqual(hash(test.example), hash(same))

    with it("has a different hash for other names and groups") as test:
        other = Example(test.name + " something else", test.example_group)
        another = Example(test.name, mock.Mock())

        test.assertNotEqual(hash(test.example), hash(other))
        test.assertNotEqual(hash(test.example), hash(another))
