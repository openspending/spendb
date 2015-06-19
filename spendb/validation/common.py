import re
from colander import Function, All, Length, null, Invalid

RESERVED_TERMS = ['entry', 'entries', 'dataset', 'datasets', 'dimension',
                  'dimensions', 'editor', 'meta', 'id', 'login', 'logout',
                  'settings', 'browser', 'explorer', 'member', 'register',
                  'after_login', 'after_logout', 'locale', 'reporterror',
                  'getinvolved', 'api', '500', 'error', 'url', 'model',
                  'distinct', 'views', 'new']


def _dataset_name(name):
    """ These are names that have a special meaning in URLs and
    cannot be used for dataset names. """
    if name is not None and name.lower() in RESERVED_TERMS:
        return "'%s' is a reserved word and cannot be used here" % name
    if not re.match(r"^[\w\_\-]+$", name):
        return ("Name must include only "
                "letters, numbers, dashes and underscores")
    if '__' in name:
        return "Double underscores are not allowed in dataset names."
    return True


dataset_name = All(Length(min=2, max=30), Function(_dataset_name))


def _field_name(name):
    """ These are names that have a special meaning in URLs and
    cannot be used for dataset names. """
    if not re.match(r"^[\w\_]+$", name):
        return ("Name must include only letters, numbers and underscores")
    if '__' in name:
        return "Double underscores are not allowed in field names."
    return True


field_name = All(Length(min=2, max=30), Function(_field_name))


def prepare_name(name):
    """ Convert a given value to a name. """
    if name is None or name is null:
        return ''
    return unicode(name).strip()


def require_one_child(data):
    if isinstance(data, dict) and len(data.keys()):
        return True
    return "Must have at least one dimension and one measure."


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
