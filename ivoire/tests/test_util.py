from unittest import TestCase

from ivoire import util
from ivoire.tests.util import PatchMixin, mock


class TestIsSpec(TestCase, PatchMixin):
    def test_specs_are_specs(self):
        self.assertTrue(util.is_spec("foo/bar/baz_spec.py"))

    def test_non_specs_are_not_specs(self):
        self.assertFalse(util.is_spec("foo/bar/baz.py"))
