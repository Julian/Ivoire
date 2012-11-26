from ivoire import describe, ContextManager
from ivoire.manager import Context
from ivoire.spec.util import ExampleWithPatch, mock


with describe(ContextManager, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.manager = ContextManager()

    with it("creates contexts") as test:
        context = test.manager.create_context("a test context")
        test.assertEqual(context, Context("a test context", test.manager))

    with it("tracks context depth") as test:
        context = test.manager.create_context("a test context")

        test.assertEqual(test.manager.context_depth, 1)

        test.manager.enter(context)
        test.assertEqual(test.manager.context_depth, 2)

        test.manager.exit(context)
        test.assertEqual(test.manager.context_depth, 1)
