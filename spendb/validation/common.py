import re
from colander import Function, All, Length, null, Invalid

RESERVED_TERMS = ['entry', 'entries', 'dataset', 'datasets', 'dimension',
                  'dimensions', 'editor', 'meta', 'id', 'login', 'logout',
                  'settings', 'browser', 'explorer', 'member', 'register',
                  'after_login', 'after_logout', 'locale', 'reporterror',
                  'getinvolved', 'api', '500', 'error', 'url', 'model',
                  'distinct', 'views', 'new']


def reserved_name(name):
    """ These are names that have a special meaning in URLs and
    cannot be used for dataset or dimension names. """
    if name is not None and name.lower() in RESERVED_TERMS:
        return "'%s' is a reserved word and cannot be used here" % name
    return True


def database_name(name):
    if not re.match(r"^[\w\_]+$", name):
        return ("Name must include only "
                "letters, numbers, dashes and underscores")
    if len(name) > 30:
        return "Names must not be longer than 30 characters."
    if '__' in name:
        return "Double underscores are not allowed in dataset names."
    return True


valid_name = All(Length(min=2), Function(reserved_name),
                 Function(database_name))


def prepare_name(name):
    """ Convert a given value to a name. """
    if name is None or name is null:
        return ''
    return unicode(name).strip()


class Ref(object):

    def deserialize(self, node, cstruct):
        if cstruct is null:
            return null
        value = self.decode(cstruct)
        if value is None:
            raise Invalid(node, 'Missing')
        return value

    def cstruct_children(self, node, cstruct):
        return []
