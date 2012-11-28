from ivoire import context, describe, ContextManager
from ivoire.manager import Context
from ivoire.spec.util import ExampleWithPatch, mock


with describe(ContextManager, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.result = mock.Mock()
        test.manager = ContextManager(test.result)
        test.context = test.manager.create_context("a test context")

    with context(context):
        with it("creates contexts") as test:
            context = test.manager.create_context("a test context")
            test.assertEqual(context, Context("a test context", test.manager))

        with it("is a bit nasty and tries to get __name__s") as test:
            def foo(): pass
            context = test.manager.create_context(foo)
            test.assertEqual(context, Context("foo", test.manager))

    with it("starts off at a global context depth of 0") as test:
        test.assertEqual(test.manager.context_depth, 0)

    with it("enters and exits contexts") as test:
        test.manager.enter(test.context)
        test.result.enterContext.assert_called_once_with(test.context, depth=1)

        test.manager.exit()
        test.result.exitContext.assert_called_once_with(depth=0)

    with it("doesn't call methods if the result doesn't know how") as test:
        del test.result.enterContext, test.result.exitContext

        test.manager.enter(test.context)
        test.manager.exit()
        test.assertFalse(test.result.method_calls)
