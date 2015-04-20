import types
from hashlib import sha1


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
