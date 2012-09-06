======
Ivoire
======

``ivoire`` is an `RSpec <http://rspec.info/>`_-like library for Python. If
you've never heard of RSpec, it's a Ruby library that is widely used, and has a
slightly different twist on how tests should look.

A small example
---------------

``ivoire`` has two modes of operation: standalone mode and transform mode. In
standalone mode, you simply write some tests, mainly using ``ivoire.describe``
(which serves the same purpose as its RSpec inspirer), and then execute them,
either as a script, or with the yet-to-be-written ``ivoire`` runner.

For instance:

::

    from ivoire import describe


    class Calculator(object):
        def add(self, x, y):
            return x + y

        def divide(self, x, y):
            return x / y


    with describe(describe) as it:
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

        with it("multiplies") as test:
            calculator = Calculator()
            test.assertEqual(calculator.multiply(2, 3), 6)


can be run with ``python test_example.py``, if you've saved it as such, and 
will produce output for the tests it runs.
