======
Ivoire
======

``ivoire`` is an `RSpec <http://rspec.info/>`_-like library for Python. If
you've never heard of RSpec, it's a Ruby library that is widely used, and has a
slightly different twist on how tests should look.


A Small Example
---------------

``ivoire`` has two modes of operation: standalone mode and transform mode. In
standalone mode, you simply write some tests using ``ivoire.describe`` and then
execute them with the included ``ivoire`` test runner.

For instance, if you run the following spec, the test output will appear on
standard error.

::

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


You can find this and other examples in the ``examples`` directory of the
source checkout, and run them with ``ivoire examples/calculator_spec.py`` after
you've installed ``ivoire``.


Running the Test Suite
----------------------

You can run ``Ivoire``'s test suite by running ``tox`` in the root of the
repository checkout, or by running ``YourFavoriteTestRunner ivoire``.

You need to have ``tox`` installed via your package manager or with
``pip install tox`` for the former.


Contributing
------------

``Ivoire`` is developed on `GitHub <http://github.com/Julian/Ivoire>`_.

Feel free to fork and submit patches or feature requests, your contributions
are most welcome!

If you'd like the best chance for them to be merged quickly try to include
tests with your pull request, and adhere to general Python coding standards and
your own common sense :).
