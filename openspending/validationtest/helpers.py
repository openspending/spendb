from nose.plugins.skip import SkipTest

import os as _os
import json

TEST_ROOT = _os.path.dirname(__file__)


def fixture_file(name):
    """Return a file-like object pointing to a named fixture."""
    return open(fixture_path(name))


def model_fixture(name):
    model_fp = fixture_file(name + '.json')
    model = json.load(model_fp)
    model_fp.close()
    return model


def fixture_path(name):
    """
    Return the full path to a named fixture.

    Use fixture_file rather than this method wherever possible.
    """
    return _os.path.join(TEST_ROOT, 'fixtures', name)


def skip(*args, **kwargs):
    raise SkipTest(*args, **kwargs)


