import re
from unidecode import unidecode

SLUG_RE = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delimiter='-'):
    '''\
    Generate an ascii only slug from the text that can be
    used in urls or as a name.
    '''
    result = []
    for word in SLUG_RE.split(unicode(text).lower()):
        result.extend(unidecode(word).split())
    return unicode(delimiter.join(result))


