from datetime import datetime, date

from lxml import html
from flask.ext.babel import format_date as _format_date
from webhelpers.html import literal
from webhelpers.markdown import markdown as _markdown
from webhelpers.text import truncate


def markdown(*args, **kwargs):
    return literal(_markdown(*args, **kwargs))


def markdown_preview(text, length=150):
    if not text:
        return ''
    try:
        md = html.fromstring(unicode(markdown(text)))
        text = md.text_content()
    except:
        pass
    if length:
        text = truncate(text, length=length, whole_word=True)
    return text.replace('\n', ' ')


def format_date(dt, format='short'):
    try:
        if isinstance(dt, datetime):
            dt = dt.date()
        assert isinstance(dt, (date, datetime))
        return _format_date(dt, format=format)
    except:
        return dt


def readable_url(url):
    if len(url) > 55:
        return url[:15] + " .. " + url[len(url) - 25:]
    return url
