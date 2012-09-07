from ivoire import describe


class Calculator(object):
    def add(self, x, y):
        return x + y

    def divide(self, x, y):
        return x / y


with describe(Calculator) as it:
    with it("adds two numbers") as test:
        calculator = Calculator()
        test.assertEqual(calculator.add(2, 4), 6)

    with it("divides two numbers") as test:
        calculator = Calculator()
        test.assertEqual(calculator.divide(8, 4), 2)

    with it("doesn't divide by zero") as test:
        calculator = Calculator()
        with test.assertRaises(ZeroDivisionError):
            calculator.divide(8, 0)

    with it("multiplies two numbers") as test:
        calculator = Calculator()
        test.assertEqual(calculator.multiply(2, 3), 6)
