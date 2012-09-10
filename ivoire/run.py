import argparse
import imp
import os.path
import sys

from ivoire import result
import ivoire


def should_color(when):
    """
    Decide whether to color output.

    """

    if when == "auto":
        return sys.stdout.isatty()
    return when == "always"


parser = argparse.ArgumentParser(description="The Ivoire test runner.")
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

    for spec in config.FilePathsOrFQNs:
        if os.path.sep in spec:
            name = os.path.basename(os.path.splitext(spec)[0])
            imp.load_source(name, spec)
        else:
            __import__(spec)


def main(arguments=None):
    arguments = parser.parse_args(arguments)
    setup(arguments)
    run(arguments)
