from ivoire import describe
from ivoire.manager import Context
from ivoire.spec.util import ExampleWithPatch, mock


with describe(Context, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.manager = mock.Mock()
        test.context = Context("a test context", test.manager)

    with it("calls its manager when used as a context manager") as test:
        with test.context:
            test.manager.enter.assert_called_once_with(test.context)
        test.manager.exit.assert_called_once_with()
