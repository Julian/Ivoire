======
Ivoire
======

|PyPI| |Pythons| |CI| |Codecov|

``ivoire`` is an `RSpec <http://rspec.info/>`_-like testing framework for
Python. It aims to bring a few minor constructs over to Python in a way that
isn't overwhelmingly disruptive or counterculture.

In case you've never heard of RSpec, it's a Ruby
`BDD <http://en.wikipedia.org/wiki/Behavior_driven_development>`_ framework
that is fairly widely used, and whose tests have a style unique from xUnit's.

.. |PyPI| image:: https://img.shields.io/pypi/v/Ivoire.svg
  :alt: PyPI version
  :target: https://pypi.org/project/Ivoire/

.. |Pythons| image:: https://img.shields.io/pypi/pyversions/Ivoire.svg
  :alt: Supported Python versions
  :target: https://pypi.org/project/Ivoire/

.. |CI| image:: https://github.com/Julian/Ivoire/workflows/CI/badge.svg
  :alt: Build status
  :target: https://github.com/Julian/Ivoire/actions?query=workflow%3ACI

.. |Codecov| image:: https://codecov.io/gh/Julian/Ivoire/branch/master/graph/badge.svg
  :alt: Codecov Code coverage
  :target: https://codecov.io/gh/Julian/Ivoire


Installation
------------

Ivoire is on `PyPI <http://pypi.python.org/pypi/ivoire>`_ and can be installed
via ``pip install ivoire`` (or via your preferred installation method).

At this point you should consider Ivoire to be experimental, and there are
likely plenty of bugs to address, so please file them as you run into them on
the `issue tracker <https://github.com/Julian/Ivoire/issues>`_.


A Small Example
---------------

To write specs using Ivoire, simply import and use ``ivoire.describe``. You can
then execute the spec using the included ``ivoire`` test runner.

Here's an example of what a specification looks like.

.. code:: python

    from ivoire import describe, context


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

        with it("multiplies two numbers") as test:
            test.assertEqual(test.calc.multiply(2, 3), 6)

        with context(Calculator.divide):
            with it("divides two numbers") as test:
                test.assertEqual(test.calc.divide(8, 4), 2)

            with it("doesn't divide by zero") as test:
                with test.assertRaises(ZeroDivisionError):
                    test.calc.divide(8, 0)


You can find this example at ``examples/calculator_spec.py``, alongside a few
others.

After installing Ivoire, running the example above with
``ivoire examples/calculator_spec.py`` should produce:

.. image:: https://github.com/Julian/Ivoire/raw/master/examples/img/calculator_spec_output.png
    :alt: spec output
    :align: center

If you'd like a more verbose output, try passing the ``-v`` command line flag.

At some point in the (hopefully very near) future, when I've sorted out an
import hook, Ivoire will also be able to be run as
``ivoire transform `which nosetests` --testmatch='(?:^|[\b_\./-])[Ss]pec'``,
which will transform specs automatically into normal ``unittest.TestCase``\s.
Work on this is in progress.


Running the Test Suite
----------------------

Ivoire's test suite is currently written mostly in itself, but it still has a
small section that is written using the standard ``unittest`` test cases.

You can run Ivoire's test suite by running ``tox`` in the root of the
repository checkout after installing ``tox`` via your package manager or with
``pip install tox``. This will run both parts of the suite.


Contributing
------------

I'm Julian Berman.

You can find me on Freenode in ``#python-testing`` and various other channels
(nick: ``tos9``) if you'd like to chat.

Ivoire is developed on `GitHub <http://github.com/Julian/Ivoire>`_.

Feel free to fork and submit patches or feature requests. Your contributions
are most welcome!

If you'd like the best chance for them to be merged quickly try to include
tests with your pull request, and adhere to general Python coding standards and
your own common sense :).
