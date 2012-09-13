import argparse
import imp
import os.path
import runpy
import sys

from ivoire import result
import ivoire

try:
    from ivoire.transform import ExampleImporter
except ImportError:
    ExampleImporter = None


def should_color(when):
    """
    Decide whether to color output.

    """

    if when == "auto":
        return sys.stdout.isatty()
    return when == "always"


def parse(argv=None):
    """
    Parse some arguments using the parser, cleaning up the resulting Namespace.

    """

    if argv is None:
        argv = sys.argv[1:]

    # Evade http://bugs.python.org/issue9253
    if not argv or argv[0] not in {"run", "transform"}:
        argv.insert(0, "run")

    arguments = _parser.parse_args(argv)
    arguments.color = should_color(arguments.color)
    return arguments


def setup(config):
    """
    Setup the environment for an example run.

    """

    formatter = result.Formatter()

    if config.color:
        formatter = result.Colored(formatter)

    current_result = result.ExampleResult(formatter)

    ivoire.current_result = current_result


def run(config):
    """
    Time to run.

    """

    if config.exitfirst:
        ivoire.current_result.failfast = True

    ivoire.current_result.startTestRun()

    for spec in config.specs:
        if os.path.sep in spec:
            name = os.path.basename(os.path.splitext(spec)[0])
            imp.load_source(name, spec)
        else:
            __import__(spec)

    ivoire.current_result.stopTestRun()


def transform(config):
    """
    Run in transform mode.

    """

    if ExampleImporter is not None:
        ExampleImporter.register()
        return runpy.run_path(config.runner)


def main(argv=None):
    arguments = parse(argv)
    setup(arguments)
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
    "-x", "--exitfirst", default=False, dest="exitfirst",
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
    "-c", "--color",
    choices=["always", "never", "auto"],
    default="auto",
    dest="color",
    help="Format colored output.",
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
