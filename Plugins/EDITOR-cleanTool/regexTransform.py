import re

from lxml.etree import tostring, fromstring, XMLSyntaxError

QUOTE_PAIRS = {
    '"': '"',
    '“': '”',
    '‘': '’',
    '„': '”',
    '‚': '’',
    '«': '»',
    '‹': '›',
    '「': '」',
    '『': '』',
}

pair_patterns = [f"{re.escape(o)}([^<>]*?){re.escape(c)}" for o, c in QUOTE_PAIRS.items()]

combined_quotes = "|".join(pair_patterns)

TAG_OR_QUOTE_REGEX = re.compile(rf'(<[^>]+>)|({combined_quotes})', re.DOTALL)


def quotes(p):
    #new stuff from chatgpt
    text = tostring(p, encoding='unicode', with_tail=False)

    def replace_func(match):
        # If Group 1 matched, it's an HTML tag (e.g. <p xmlns="...">) -> keep as-is
        if match.group(1):
            return match.group(1)

        # Otherwise, Group 2 matched a quote pair in text content -> wrap in <q>
        groups = match.groups()
        inner_content = next(g for g in groups[2:] if g is not None)
        return f'<q>{inner_content}</q>'

    text = TAG_OR_QUOTE_REGEX.sub(replace_func, text)

    try:
        return fromstring(text.encode('utf-8'))
    except etree.XMLSyntaxError:
        print(text)
        raise
