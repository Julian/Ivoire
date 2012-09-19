from ivoire import describe

from ivoire import run
from ivoire.spec.util import mock, patch, patchObject


with describe(run.should_color) as it:
    @it.before
    def before(test):
        test.stderr = patchObject(test, run.sys, "stderr")

    with it("colors whenever stderr is a tty") as test:
        test.stderr.isatty.return_value = True
        test.assertTrue(run.should_color("auto"))

    with it("doesn't color otherwise") as test:
        test.stderr.isatty.return_value = False
        test.assertFalse(run.should_color("auto"))


with describe(run.run) as it:
    @it.before
    def before(test):
        test.config = mock.Mock(specs=[])
        test.result = patch(test, "ivoire.current_result")
        test.exit = patchObject(test, run.sys, "exit")

    with it("succeeds with status code 0") as test:
        test.result.wasSuccessful.return_value = True
        run.run(test.config)
        test.exit.assert_called_once_with(0)

    with it("fails with status code 1") as test:
        test.result.wasSuccessful.return_value = False
        run.run(test.config)
        test.exit.assert_called_once_with(1)
