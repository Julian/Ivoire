from ivoire import describe

from ivoire import run
from ivoire.tests.util import mock


with describe(run.should_color) as it:
    with it("colors whenever stderr is a tty") as test:
        with mock.patch.object(run.sys, "stderr"):
            run.sys.stderr.isatty.return_value = True
            test.assertTrue(run.should_color("auto"))

    with it("doesn't color otherwise") as test:
        with mock.patch.object(run.sys, "stderr"):
            run.sys.stderr.isatty.return_value = False
            test.assertFalse(run.should_color("auto"))


with describe(run.run) as it:
    with it("succeeds with status code 0") as test:
        config = mock.Mock(specs=[])

        with mock.patch("ivoire.current_result") as result:
            with mock.patch.object(run.sys, "exit") as exit:
                result.wasSuccessful.return_value = True
                run.run(config)
                exit.assert_called_once_with(0)

    with it("fails with status code 1") as test:
        config = mock.Mock(specs=[])

        with mock.patch("ivoire.current_result") as result:
            with mock.patch.object(run.sys, "exit") as exit:
                result.wasSuccessful.return_value = False
                run.run(config)
                exit.assert_called_once_with(1)
