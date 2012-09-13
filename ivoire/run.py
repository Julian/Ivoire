import argparse
import imp
import os.path
import runpy
import sys

from ivoire import result
import ivoire

try:
    from ivoire.transform import ExampleImporter
except (AttributeError, ImportError):
    ExampleImporter = None


def should_color(when):
    """
    Decide whether to color output.

    """

    if when == "auto":
        return sys.stdout.isatty()
    return when == "always"


parser = argparse.ArgumentParser(description="The Ivoire test runner.")
parser.add_argument(
    "transform",
    nargs=argparse.REMAINDER,
    help="Run an Ivoire spec through another test runner by translating its "
         "source code.",
)
parser.add_argument("FilePathsOrFQNs", nargs="+")
parser.add_argument(
    "--color",
    choices=["always", "never", "auto"],
    default="auto",
    dest="color",
    help="Format colored output.",
)
parser.add_argument(
    "-x", "--exitfirst", default=False, dest="exitfirst",
    help="Exit after the first error or failure.",
)


def setup(config):
    """
    Setup the environment for an example run.

    """

    formatter = result.Formatter()

    if should_color(config.color):
        formatter = result.Colored(formatter)

    current_result = result.ExampleResult(formatter)

    if config.exitfirst:
        current_result.failfast = True

    ivoire.current_result = current_result


def run(config):
    """
    Time to run.

    """

    ivoire.current_result.startTestRun()

    for spec in config.FilePathsOrFQNs:
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
        return runpy.run_path(config.FilePathsOrFQNs[0])


def main(arguments=None):
    arguments = parser.parse_args(arguments)
    setup(arguments)

    if arguments.transform:
        transform(arguments)
    else:
        run(arguments)
