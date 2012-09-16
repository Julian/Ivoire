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
