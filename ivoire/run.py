"""
The implementation of the Ivoire runner.

"""

import argparse
import runpy
import sys

from ivoire import result
from ivoire.load import load_by_name
from ivoire.transform import ExampleLoader, transform_possible
import ivoire


FORMATTERS = {
    "dots" : result.DotsFormatter,
}


class _ExampleNotRunning(object):
    """
    An error occurred, but no example was running. Mimic an Example object.

    """

    failureException = None
    group = None

    def __str__(self):
        return "<not in example>"


def should_color(when):
    """
    Decide whether to color output.

    """

    if when == "auto":
        return sys.stderr.isatty()
    return when == "always"


def parse(argv=None):
    """
    Parse some arguments using the parser.

    """

    if argv is None:
        argv = sys.argv[1:]

    # Evade http://bugs.python.org/issue9253
    if not argv or argv[0] not in {"run", "transform"}:
        argv = ["run"] + argv

    arguments = _clean(_parser.parse_args(argv))
    return arguments


def _clean(arguments):
    if hasattr(arguments, "color"):
        arguments.color = should_color(arguments.color)
    return arguments


def setup(config):
    """
    Setup the environment for an example run.

    """

    formatter = config.Formatter()

    if config.verbose:
        formatter = result.Verbose(formatter)
    if config.color:
        formatter = result.Colored(formatter)

    current_result = result.ExampleResult(formatter)

    ivoire.current_result = ivoire._manager.result = current_result


def run(config):
    """
    Time to run.

    """

    setup(config)

    if config.exitfirst:
        ivoire.current_result.failfast = True

    ivoire.current_result.startTestRun()

    for spec in config.specs:
        try:
            load_by_name(spec)
        except Exception:
            ivoire.current_result.addError(
                _ExampleNotRunning(), sys.exc_info()
            )

    ivoire.current_result.stopTestRun()

    sys.exit(not ivoire.current_result.wasSuccessful())


def transform(config):
    """
    Run in transform mode.

    """

    if transform_possible:
        ExampleLoader.register()

        args, sys.argv[1:] = sys.argv[1:], config.args
        try:
            return runpy.run_path(config.runner, run_name="__main__")
        finally:
            sys.argv[1:] = args


def main(argv=None):
    arguments = parse(argv)
    arguments.func(arguments)


_parser = argparse.ArgumentParser(description="The Ivoire test runner.")
_subparsers = _parser.add_subparsers()

_run = _subparsers.add_parser(
    "run",
    help="Run Ivoire specs."
)
_run.add_argument(
    "-c", "--color",
    choices=["always", "never", "auto"],
    default="auto",
    dest="color",
    help="Format colored output.",
)
_run.add_argument(
    "-f", "--formatter",
    choices=FORMATTERS,
    default="dots",
    dest="Formatter",
    type=lambda formatter : FORMATTERS[formatter],
    help="Format output with the given formatter.",
)
_run.add_argument(
    "-v", "--verbose",
    action="store_true",
    help="Format verbose output.",
)
_run.add_argument(
    "-x", "--exitfirst",
    action="store_true",
    help="Exit after the first error or failure.",
)
_run.add_argument("specs", nargs="+")
_run.set_defaults(func=run)

_transform = _subparsers.add_parser(
    "transform",
    help="Run an Ivoire spec through another test runner by translating its "
         "source code.",
)
_transform.add_argument(
    "runner",
    help="The command to run the transformed tests with."
)
_transform.add_argument(
    "args",
    nargs=argparse.REMAINDER,
)
_transform.set_defaults(func=transform)
