import types
from hashlib import sha1
from slugify import slugify # noqa


def flatten(data, sep='.'):
    out = {}
    for k, v in data.items():
        ksep = k + sep
        if isinstance(v, dict):
            for ik, iv in flatten(v, sep).items():
                out[ksep + ik] = iv
        else:
            out[k] = v
    return out


def nestify(data):
    """ Cubes returns entries and aggregation results in a non-nested way
    with a dotted notation for key names. This function turns that format
    into a set of nested dictionaries. """
    nested = {}
    for key, value in data.items():
        path = key.split('.')
        out = nested
        for i, level in enumerate(path):
            if i == len(path) - 1:
                out[level] = value
            elif level not in out:
                out[level] = {}
            out = out[level]
    return nested


def hash_values(iterable):
    """Return a cryptographic hash of an iterable."""
    return sha1(''.join(sha1(unicode(val).encode('utf-8')).hexdigest()
                        for val in iterable)).hexdigest()


def cache_hash(*a, **kw):
    """ Try to hash an arbitrary object for caching. """

    def cache_str(o):
        if isinstance(o, (types.FunctionType, types.BuiltinFunctionType,
                          types.MethodType, types.BuiltinMethodType,
                          types.UnboundMethodType)):
            return getattr(o, 'func_name', 'func')
        if isinstance(o, dict):
            o = [k + ':' + cache_str(v) for k, v in o.items()]
        if isinstance(o, (list, tuple, set)):
            o = sorted(map(cache_str, o))
            o = '|'.join(o)
        if isinstance(o, basestring):
            return o
        if hasattr(o, 'updated_at'):
            return cache_str((repr(o), o.updated_at))
        return repr(o)

    hash = cache_str((a, kw)).encode('utf-8')
    return sha1(hash).hexdigest()
