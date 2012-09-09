import argparse
import imp
import os.path


parser = argparse.ArgumentParser(description="The Ivoire test runner.")
parser.add_argument("FilePathsOrFQNs", nargs="+")


def main(arguments=None):
    arguments = parser.parse_args(arguments)
    for spec in arguments.FilePathsOrFQNs:
        if os.path.sep in spec:
            name = os.path.basename(os.path.splitext(spec)[0])
            imp.load_source(name, spec)
        else:
            __import__(spec)
