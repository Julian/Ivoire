from ivoire import Example
from ivoire.tests.util import _cleanUpPatch, mock


class ExampleWithPatch(Example):
    patch = _cleanUpPatch(mock.patch)
    patchDict = _cleanUpPatch(mock.patch.dict)
    patchObject = _cleanUpPatch(mock.patch.object)
