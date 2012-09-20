from __future__ import print_function
from textwrap import dedent
from unittest import TestCase, skipIf
import ast

from ivoire import transform
from ivoire.tests.util import PatchMixin, mock


class TestRegistration(TestCase, PatchMixin):
    def setUp(self):
        self.FileFinder = self.patchObject(transform, "FileFinder")
        self.hooks = ()
        self.path_hooks = self.patchObject(
            transform.sys, "path_hooks", list(self.hooks)
        )

    def test_it_registers_a_file_finder(self):
        transform.ExampleLoader.register()
        self.assertEqual(
            self.path_hooks,
            list(self.hooks) + [self.FileFinder.path_hook.return_value],
        )
        self.FileFinder.path_hook.assert_called_once_with(
            (transform.ExampleLoader, ["_spec.py"]),
        )

    def test_it_unregisters_the_file_finder(self):
        transform.ExampleLoader.register()
        transform.ExampleLoader.unregister()
        self.assertEqual(self.path_hooks, list(self.hooks))


class TestExampleLoader(TestCase, PatchMixin):
    @skipIf(
        not transform.transform_possible,
        "Transformation isn't supported yet on this version.",
    )
    def test_it_transforms_the_source(self):
        trans = self.patchObject(transform.ExampleTransformer, "transform")
        parse = self.patchObject(ast, "parse")
        compile = self.patchObject(transform, "compile", create=True)

        fullname, path = mock.Mock(), mock.Mock()
        source, path = mock.Mock(), mock.Mock()

        loader = transform.ExampleLoader(fullname, path)
        code = loader.source_to_code(source, path)

        self.assertEqual(code, compile.return_value)
        compile.assert_called_once_with(
            trans.return_value, path, "exec", dont_inherit=True
        )
        trans.assert_called_once_with(parse.return_value)
