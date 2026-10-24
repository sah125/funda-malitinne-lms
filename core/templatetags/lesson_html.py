"""Safe rendering of imported lesson HTML.

Lessons imported from Word are stored as HTML (prefixed with <!--html-->).
Before showing them we strip anything that is not on a short allow-list, so a
lesson can never run scripts in a learner's browser.
"""
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlparse

from django import template
from django.utils.html import linebreaks
from django.utils.safestring import mark_safe

from core.importers import LESSON_MARKER

register = template.Library()

ALLOWED_TAGS = {'p', 'br', 'h2', 'h3', 'h4', 'ul', 'ol', 'li', 'strong', 'b', 'em', 'i', 'u', 'blockquote',
                'table', 'thead', 'tbody', 'tr', 'th', 'td', 'div', 'span', 'figure', 'figcaption', 'img', 'a', 'hr'}
VOID = {'br', 'img', 'hr'}
ALLOWED_ATTRS = {'a': {'href', 'title'}, 'img': {'src', 'alt', 'loading'}, 'td': {'colspan', 'rowspan'},
                 'th': {'colspan', 'rowspan'}, 'div': {'class'}, 'span': {'class'}}
SAFE_CLASSES = {'table-wrap', 'lesson-topic-intro', 'callout', 'tip'}


def _safe_url(url, allow_relative=True):
    url = (url or '').strip()
    parsed = urlparse(url)
    if parsed.scheme in ('http', 'https', 'mailto'):
        return url
    if allow_relative and not parsed.scheme and not url.startswith('//'):
        return url
    return None


class _Sanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.stack, self.skip = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'iframe', 'object', 'embed'):
            self.skip += 1
            return
        if self.skip or tag not in ALLOWED_TAGS:
            return
        kept = []
        for name, value in attrs:
            if name not in ALLOWED_ATTRS.get(tag, set()):
                continue
            if name in ('href', 'src'):
                value = _safe_url(value)
                if value is None:
                    continue
            if name == 'class':
                value = ' '.join(c for c in (value or '').split() if c in SAFE_CLASSES)
                if not value:
                    continue
            kept.append(f' {name}="{escape(value or "", quote=True)}"')
        if tag == 'a':
            kept.append(' rel="noopener nofollow" target="_blank"')
        self.out.append(f'<{tag}{"".join(kept)}>')
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'iframe', 'object', 'embed'):
            self.skip = max(0, self.skip - 1)
            return
        if self.skip or tag not in ALLOWED_TAGS or tag in VOID:
            return
        if tag in self.stack:
            while self.stack:
                t = self.stack.pop()
                self.out.append(f'</{t}>')
                if t == tag:
                    break

    def handle_data(self, data):
        if not self.skip:
            self.out.append(escape(data))

    def result(self):
        while self.stack:
            self.out.append(f'</{self.stack.pop()}>')
        return ''.join(self.out)


def sanitize(value):
    parser = _Sanitizer()
    parser.feed(value or '')
    parser.close()
    return parser.result()


@register.filter
def lesson_body(content):
    """Imported (HTML) lessons are sanitised; plain-text lessons keep line breaks."""
    content = content or ''
    if content.lstrip().startswith(LESSON_MARKER):
        return mark_safe('<div class="lesson-prose">' + sanitize(content) + '</div>')
    return mark_safe('<div class="lesson-prose">' + linebreaks(escape(content)) + '</div>')
