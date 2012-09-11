"""
A spec for the next() standard library function.

"""

from ivoire import describe


with describe(next) as it:
    with it("returns the next element of an iterable") as test:
        iterable = iter(range(5))
        test.assertEqual(next(iterable), 0)

    with it("raises StopIteration if no elements are found") as test:
        with test.assertRaises(StopIteration):
            next(iter([]))

    with it("returns default instead of StopIteration if given") as test:
        default = "a default"
        test.assertEqual(next(iter([]), default), default)
