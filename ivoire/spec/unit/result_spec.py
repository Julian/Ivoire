from ivoire import describe, result
from ivoire.compat import indent
from ivoire.spec.util import ExampleWithPatch, mock


with describe(result.Verbose, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.exc_info = mock.Mock()
        test.formatter = mock.Mock()
        test.result = mock.Mock()
        test.test = mock.Mock()
        test.verbose = result.Verbose(test.formatter)

    with it("delegates to the formatter") as test:
        test.assertEqual(test.verbose.foo, test.formatter.foo)

    with it("finishes with a newline") as test:
        test.verbose.finished()
        test.formatter.show.assert_called_once_with("\n")

    with it("formats errors") as test:
        test.verbose.maybe_show_group = mock.Mock()
        test.assertEqual(
            test.verbose.error(test.test, test.exc_info),
            "    {} - ERROR\n".format(test.test)
        )
        test.verbose.maybe_show_group.assert_called_once_with(test.test.group)

    with it("formats failures") as test:
        test.verbose.maybe_show_group = mock.Mock()
        test.assertEqual(
            test.verbose.failure(test.test, test.exc_info),
            "    {} - FAIL\n".format(test.test)
        )
        test.verbose.maybe_show_group.assert_called_once_with(test.test.group)

    with it("formats successes") as test:
        test.verbose.maybe_show_group = mock.Mock()
        test.assertEqual(
            test.verbose.success(test.test), "    {}\n".format(test.test)
        )
        test.verbose.maybe_show_group.assert_called_once_with(test.test.group)


with describe(result.Verbose.maybe_show_group, Example=ExampleWithPatch) as it:
    @it.before
    def before(test):
        test.formatter = mock.Mock()
        test.test = mock.Mock()
        test.verbose = result.Verbose(test.formatter)

    with it("shows newly seen groups") as test:
        test.verbose.maybe_show_group(test.test.group)
        test.verbose.show.assert_called_once_with(str(test.test.group) + "\n")

    with it("doesn't show old groups") as test:
        test.verbose.maybe_show_group(test.test.group)

        test.verbose.maybe_show_group(test.test.group)
        test.assertEqual(test.verbose.show.call_count, 1)
