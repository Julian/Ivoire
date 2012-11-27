from ivoire import describe, ContextManager
from ivoire.manager import Context
from ivoire.spec.util import ExampleWithPatch, mock


with describe(ContextManager, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.result = mock.Mock()
        test.manager = ContextManager(test.result)
        test.context = test.manager.create_context("a test context")

    with it("creates contexts") as test:
        context = test.manager.create_context("a test context")
        test.assertEqual(context, Context("a test context", test.manager))

    with it("starts off at a global context depth of 1") as test:
        test.assertEqual(test.manager.context_depth, 1)

    with it("enters and exits contexts") as test:
        test.manager.enter(test.context)
        test.result.enterContext.assert_called_once_with(test.context, depth=2)

        test.manager.exit()
        test.result.exitContext.assert_called_once_with(depth=1)

    with it("doesn't call methods if the result doesn't know how") as test:
        del test.result.enterContext, test.result.exitContext

        test.manager.enter(test.context)
        test.manager.exit()
        test.assertFalse(test.result.method_calls)
