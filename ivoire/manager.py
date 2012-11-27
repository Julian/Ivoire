class ContextManager(object):
    def __init__(self, result):
        self.context_depth = 1
        self.result = result

    def create_context(self, name):
        return Context(name, self)

    def enter(self, context):
        self.context_depth += 1

        enterContext = getattr(self.result, "enterContext", None)
        if enterContext is not None:
            enterContext(context, depth=self.context_depth)

    def exit(self):
        self.context_depth -= 1

        exitContext = getattr(self.result, "exitContext", None)
        if exitContext is not None:
            exitContext(depth=self.context_depth)


class Context(object):
    def __init__(self, name, manager):
        self.manager = manager
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.name == other.name

    def __ne__(self, other):
        return not self == other

    def __enter__(self):
        """
        Enter the context.

        """

        self.manager.enter(self)

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context.

        """

        self.manager.exit()
