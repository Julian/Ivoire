"""
A simple calculator specification.

"""

from ivoire import describe


class Calculator(object):
    def add(self, x, y):
        return x + y

    def divide(self, x, y):
        return x / y


with describe(Calculator) as it:
    @it.before
    def before(test):
        test.calc = Calculator()

    with it("adds two numbers") as test:
        test.assertEqual(test.calc.add(2, 4), 6)

    with it("divides two numbers") as test:
        test.assertEqual(test.calc.divide(8, 4), 2)

    with it("doesn't divide by zero") as test:
        with test.assertRaises(ZeroDivisionError):
            test.calc.divide(8, 0)

    with it("multiplies two numbers") as test:
        test.assertEqual(test.calc.multiply(2, 3), 6)
