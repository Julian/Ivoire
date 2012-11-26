class ContextManager(object):
    context_depth = 1

    def create_context(self, name):
        return Context(name, self)

    def enter(self, context):
        self.context_depth += 1

    def exit(self, context):
        self.context_depth -= 1


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

        self.manager.exit(self)
