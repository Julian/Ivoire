from __future__ import print_function
from textwrap import dedent
from unittest import TestCase
import ast
import copy

from ivoire import describe, transform
from ivoire.spec.util import ExampleWithPatch, mock


def dump(node):  # pragma: no cover
    return(dedent("""
    --- Dumping Node ---

    {}

    --- End ---
    """.format(ast.dump(node))))


with describe(transform.ExampleTransformer, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.transformer = transform.ExampleTransformer()

    def execute(test, source):
        test.globals, test.locals = {}, {}
        test.node = ast.parse(dedent(source))
        test.transformed = test.transformer.transform(test.node)
        compiled = compile(test.transformed, "<testing transform>", "exec")

        try:
            exec(compiled, test.globals, test.locals)
        except Exception:  # pragma: no cover
            print(dump(test.transformed))
            raise

    def assertNotTransformed(test, source):
        node = ast.parse(dedent(source))
        transformed = test.transformer.transform(copy.deepcopy(node))
        # TODO: Ugly! Fix me please. See http://bugs.python.org/issue15987
        test.assertEqual(ast.dump(node), ast.dump(transformed))

    with it("fixes missing line numbers") as test:
        fix = test.patchObject(transform.ast, "fix_missing_locations")
        node = ast.Pass()
        test.transformer.transform(node)
        fix.assert_called_once_with(node)

    with it("transforms ivoire imports to unittest imports") as test:
        execute(test, "from ivoire import describe")
        test.assertEqual(test.locals, {"TestCase" : TestCase})

    with it("leaves other imports alone") as test:
        assertNotTransformed(test, "from textwrap import dedent")

    with it("transforms uses of describe to TestCases") as test:
        test.skip_if(
            not transform.transform_possible,
            "Transform not available on this version."
        )

        execute(test, """
            from ivoire import describe
            with describe(next) as it:
                with it("returns the next element") as test:
                    test.i = [1, 2, 3]
                    test.assertEqual(next(test.i), 1)
        """)

        TestNext = test.locals["TestNext"]
        test = TestNext("test_it_returns_the_next_element")
        test.run()
        test.assertEqual(test.i, [1, 2, 3])

    with it("leaves other context managers alone") as test:
        test.skip_if(
            not transform.transform_possible,
            "Transform not available on this version."
        )

        assertNotTransformed(test, """
            from warnings import catchwarnings
            with catchwarnings() as thing:
                with catchwarnings():
                    pass
        """)
