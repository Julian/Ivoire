from functools import wraps

try:
    from unittest import mock
except ImportError:
    import mock


def _cleanUpPatch(fn):
    @wraps(fn)
    def cleaned(test, *args, **kwargs):
        patch = fn(*args, **kwargs)
        test.addCleanup(patch.stop)
        return patch.start()
    return cleaned


patch = _cleanUpPatch(mock.patch)
patchDict = _cleanUpPatch(mock.patch.dict)
patchObject = _cleanUpPatch(mock.patch.object)
