from . import helper
from .attributes import attributes
from .regexTransform import quotes

from lxml import etree

def do_body(raw, css):
    for comment in raw.xpath('//comment()'):
        comment.getparent().remove(comment)

    body = raw.xpath("//*[local-name()='body']")[0]
    index = 0

    while index < len(body):
        element = body[index]

        tag = helper.ln(element)

        if tag in ('div', 'span', 'svg'):
            if element.text:
                element.tag = 'p'
            helper.unwrap(element)
            continue

        if tag == 'image':
            img = etree.Element('img')
            for key, attr in element.attrib.items():
                if key.lower().endswith(('href', 'src')):
                    img.set('src',attr)

            parent = element.getparent()
            position = parent.index(element)
            parent.remove(element)
            parent.insert(position, img)

            index += 1
            continue

        if tag in ['br', 'button']:
            body.remove(element)
            continue

        if tag in ('img', 'a'):
            index += 1
            continue

        if not ''.join(element.itertext()).strip():
            if element.xpath('.//*[local-name()="img" or local-name()="image"]'):
                helper.unwrap(element)
                continue
            else:
                body.remove(element)
                continue

        if attributes(element, raw, css):
            index -= 1
            continue

        for span in element.xpath('.//*[local-name()="span"]'):
            span_id = span.get("id")
            parent = span.getparent()

            if parent is not None:
                if span_id:
                    parent.set("id", span_id)

                helper.unwrap(span)
                
        replacement = quotes(element)
        body[index] = replacement
        index += 1

    # First Element = h1 if not img
    element = body[0]
    tag = helper.ln(element)
    if tag not in ('img', 'a'):
        element.tag = 'h1'
    return 0