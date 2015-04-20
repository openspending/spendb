from ordereddict import OrderedDict
import hashlib

from spendb.reference import CATEGORIES, COUNTRIES, LANGUAGES


class ParamParser(object):
    defaults = OrderedDict()
    defaults['page'] = 1
    defaults['pagesize'] = 10000
    defaults['order'] = None

    def __init__(self, params):
        self.params = self.defaults.copy()
        self.params.update(params)

    def parse(self):
        self._output = {}
        self._errors = []

        for key in self.params.keys():
            if key not in self.defaults:
                continue

            parser = 'parse_{0}'.format(key)
            if hasattr(self, parser):
                result = getattr(self, parser)(self.params[key])
            else:
                result = self.params[key]

            if result is not None:
                self._output[key] = result

        return self._output, self._errors

    def key(self):
        params = sorted(self.params.items())
        return hashlib.sha1(repr(params)).hexdigest()

    def _error(self, msg):
        self._errors.append(msg)

    def parse_page(self, page):
        return max(1, self._to_float('page', page))

    def parse_pagesize(self, pagesize):
        return self._to_int('pagesize', pagesize)

    def parse_order(self, order):
        if not order:
            return []

        result = []
        for part in order.split('|'):
            try:
                dimension, direction = part.split(':')
            except ValueError:
                self._error('Wrong format for "order". It has to be '
                            'specified with request parameters in the form '
                            '"order=dimension:direction|dimension:direction". '
                            'We got: "order=%s"' % order)
                return
            else:
                if direction not in ('asc', 'desc'):
                    self._error('Order direction can be "asc" or "desc". We '
                                'got "%s" in "order=%s"' %
                                (direction, order))
                    return

                if direction == 'asc':
                    reverse = False
                else:
                    reverse = True

                result.append((dimension, reverse))
        return result

    def _to_float(self, name, value):
        try:
            return float(value)
        except ValueError:
            self._error('"%s" has to be a number, it is: %s' %
                        (name, value))

    def _to_int(self, name, value):
        try:
            return int(value)
        except ValueError:
            self._error('"%s" has to be an integer, it is: %s' %
                        (name, value))

    def _to_bool(self, value):
        return value.lower().strip() in ['true', '1', 'yes', 'on']


class DatasetIndexParamParser(ParamParser):

    """
    Parameter parser for the dataset index page (which is served
    differently based on languages, territories and category chosen.
    """

    # We cannot use the defaults from ParamParser since that includes
    # order.
    defaults = OrderedDict()
    defaults['languages'] = []
    defaults['territories'] = []
    defaults['category'] = None
    # Used for pagination in html pages only
    defaults['page'] = 1
    defaults['pagesize'] = 25

    def __init__(self, params):
        """
        Initialize dataset index parameter parser, and make
        the initial params available as part of the instance
        """
        self.request_params = params
        super(DatasetIndexParamParser, self).__init__(params)

    def parse_languages(self, language):
        """
        Get the languages. This ignores the language supplied since multiple
        languages can be provided with multiple parameters and ParamParser
        does not support that.
        """
        # We force the language codes to lowercase and strip whitespace
        languages = [l.lower().strip()
                     for l in self.request_params.getlist('languages')]
        # Check if this language is supported by SpenDB
        # If not we add an error
        for lang in languages:
            if lang.lower().strip() not in LANGUAGES:
                self._error('Language %s not found' % lang)

        return languages

    def parse_territories(self, territory):
        """
        Get the territories. This ignores the territory supplied since multiple
        territories can be provided with multiple parameters and ParamParser
        does not support that.
        """
        # We force the territory codes to uppercase and strip whitespace
        # Isn't it great that we're so consistent with uppercase and lowercase
        # (uppercase here, lowercase in languages and categories)
        territories = [t.upper().strip()
                       for t in self.request_params.getlist('territories')]

        # Check if this territory is supported by SpenDB
        # If not we add an error
        for country in territories:
            if country not in COUNTRIES:
                self._error('Territory %s not found' % country)

        return territories

    def parse_category(self, category):
        """
        Get the category and check if it exists in
        supported categories. If so we return it.
        """
        if category:
            # We want the category to be lowercase and stripped of whitespace
            category = category.lower().strip()
            # Check if category is supported, if not add an error
            if category in CATEGORIES:
                return category
            else:
                self._error('Category %s not found' % category)

        # We return None if there's an error of no category
        return None


class DistinctParamParser(ParamParser):
    defaults = ParamParser.defaults.copy()
    defaults['q'] = ''
    defaults['page'] = 1
    defaults['pagesize'] = 100

    def parse_pagesize(self, pagesize):
        return min(100, self._to_int('pagesize', pagesize))
