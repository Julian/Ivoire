"""
Ivoire is an RSpec-like testing framework for Python.

Globals defined in this module:
    current_result: Should be set by a runner to an object that has the same
                    interface as unittest.TestResult. It will be used by every
                    example that is instantiated to record test results during
                    the runtime of Ivoire.

    __version__: The current version information

"""

from ivoire.standalone import Example, describe


__version__ = "0.1"

current_result = None
