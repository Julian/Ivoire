from unittest import TestCase

from ivoire import run
from ivoire.tests.util import PatchMixin, mock


class TestMain(TestCase, PatchMixin):
    def test_parses_and_loads_specs(self):
        imp = self.patchObject(run, "imp")
        importfn = self.patchObject(run, "__import__", create=True)

        run.main(["foo.bar", "foo/bar/baz.py", "foo"])

        self.assertEqual(
            importfn.mock_calls, [mock.call("foo.bar"), mock.call("foo")],
        )
        imp.load_source.assert_called_once_with("baz", "foo/bar/baz.py")
