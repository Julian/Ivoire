"""
Spec results for Ivoire specs.
"""
from textwrap import indent
from unittest import TestResult
import sys
import time


class ExampleResult(TestResult):
    """
    Track the outcomes of example runs.

    """

    def __init__(self, formatter):
        super().__init__()
        self.formatter = formatter

    def startTestRun(self):
        super().startTestRun()
        self._start = time.time()

    def enterContext(self, context, depth):
        self.formatter.show(self.formatter.enter_context(context, depth))

    def exitContext(self, depth):
        self.formatter.show(self.formatter.exit_context(depth))

    def enterGroup(self, group):
        self.formatter.show(self.formatter.enter_group(group))

    def addError(self, example, exc_info):
        super().addError(example, exc_info)
        self.formatter.show(self.formatter.error(example, exc_info))

    def addFailure(self, example, exc_info):
        super().addFailure(example, exc_info)
        self.formatter.show(self.formatter.failure(example, exc_info))

    def addSuccess(self, example):
        super().addSuccess(example)
        self.formatter.show(self.formatter.success(example))

    def addSkip(self, example, reason):
        super().addSkip(example, reason)
        self.formatter.show(self.formatter.skip(example, reason))

    def exitGroup(self, group):
        self.formatter.show(self.formatter.exit_group(group))

    def stopTestRun(self):
        super().stopTestRun()
        self.elapsed = time.time() - self._start

        self.formatter.finished()
        self.formatter.show(self.formatter.errors(self.errors))
        self.formatter.show(self.formatter.failures(self.failures))
        self.formatter.show(
            self.formatter.statistics(elapsed=self.elapsed, result=self),
        )


class FormatterMixin:
    """
    Provide some higher-level formatting using the child's building blocks.

    """

    def finished(self):
        """
        The run has finished.
        """
        self.show("\n\n")

    def statistics(self, elapsed, result):
        """
        Return output for the combined time and result summary statistics.
        """
        return "\n".join((self.timing(elapsed), self.result_summary(result)))

    def errors(self, errors):
        if not errors:
            return ""

        tracebacks = (self.traceback(error, tb) for error, tb in errors)
        return "\n".join(["Errors:\n", "\n".join(tracebacks), ""])

    def failures(self, failures):
        if not failures:
            return ""

        tracebacks = (self.traceback(fail, tb) for fail, tb in failures)
        return "\n".join(["Failures:\n", "\n".join(tracebacks), ""])


class Colored(FormatterMixin):
    """
    Wrap a formatter to show colored output.

    """

    ANSI = {  # noqa: RUF012
        "reset": "\x1b[0m",
        "black": "\x1b[30m",
        "red": "\x1b[31m",
        "green": "\x1b[32m",
        "yellow": "\x1b[33m",
        "blue": "\x1b[34m",
        "magenta": "\x1b[35m",
        "cyan": "\x1b[36m",
        "gray": "\x1b[37m",
    }

    def __init__(self, formatter):
        self._formatter = formatter

    def __getattr__(self, attr):
        """
        Delegate to the wrapped formatter.
        """
        return getattr(self._formatter, attr)

    def color(self, color, text):
        """
        Color some text in the given ANSI color.
        """
        return "{escape}{text}{reset}".format(
            escape=self.ANSI[color],
            text=text,
            reset=self.ANSI["reset"],
        )

    def error(self, example, exc_info):
        return self.color("red", self._formatter.error(example, exc_info))

    def failure(self, example, exc_info):
        return self.color("red", self._formatter.failure(example, exc_info))

    def success(self, example):
        return self.color("green", self._formatter.success(example))

    def traceback(self, example, traceback):
        name = str(example.group) + ": " + str(example)
        colored = "\n".join([self.color("blue", name), traceback])
        return indent(colored, 4 * " ")

    def result_summary(self, result):
        output = self._formatter.result_summary(result)

        if result.wasSuccessful():
            return self.color("green", output)
        return self.color("red", output)


class DotsFormatter(FormatterMixin):
    """
    A formatter which uses dots to represent specs.
    """

    def __init__(self, stream=sys.stderr):
        self.stream = stream

    def show(self, text):
        """
        Write the text to the stream and flush immediately.
        """
        self.stream.write(text)
        self.stream.flush()

    def enter_context(self, context, depth):
        """
        A new context was entered.
        """
        return ""

    def exit_context(self, depth):
        """
        A context was exited.
        """
        return ""

    def enter_group(self, group):
        """
        A new example group was entered.
        """
        return ""

    def exit_group(self, group):
        """
        The example group was entered.
        """
        return ""

    def result_summary(self, result):
        """
        Return a summary of the results.
        """
        return "{} examples, {} errors, {} failures\n".format(
            result.testsRun,
            len(result.errors),
            len(result.failures),
        )

    def timing(self, elapsed):
        """
        Return output on the time taken on the examples run.
        """
        return f"Finished in {elapsed:.6f} seconds.\n"

    def error(self, example, exc_info):
        """
        An error was encountered.
        """
        return "E"

    def failure(self, example, exc_info):
        """
        A failure was encountered.
        """
        return "F"

    def skip(self, example, reason):
        """
        A skip was encountered.
        """
        return "S"

    def success(self, example):
        """
        A success was encountered.
        """
        return "."

    def traceback(self, example, traceback):
        """
        Format an example and its traceback.
        """
        return "\n".join((str(example), traceback))


class Verbose(FormatterMixin):
    """
    Show verbose output (including example and group descriptions).

    """

    def __init__(self, formatter):
        self._depth = 1
        self._formatter = formatter

    def __getattr__(self, attr):
        return getattr(self._formatter, attr)

    def enter_context(self, context, depth):
        self._depth = depth + 1
        return indent(context.name + "\n", depth * 4 * " ")

    def exit_context(self, depth):
        self._depth = depth + 1
        return ""

    def enter_group(self, group):
        return f"{group}\n"

    def finished(self):
        self.show("\n")

    def error(self, example, exc_info):
        return indent(str(example), self._depth * 4 * " ") + " - ERROR\n"

    def failure(self, example, exc_info):
        return indent(str(example), self._depth * 4 * " ") + " - FAIL\n"

    def success(self, example):
        return indent(str(example), self._depth * 4 * " ") + "\n"
