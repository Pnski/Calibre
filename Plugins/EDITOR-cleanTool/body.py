from . import helper

from .regexTransform import quotes

def do_body(raw, cssClasses):
    counter = {
        'deleted' : 0,
        'images' : 0,
    }

    validFonts = " or ".join([
        f"contains(@style, '{font}')"
        for font in [
            "serif",
            "sans-serif",
            "monospace",
            "times new roman",
            "arial",
        ]
    ])

    # delete uneccessary bloat, not visible stuff
    for delCondition in [
        "local-name()='br'",
        "local-name()='button'",
        "contains(@style, 'overflow:hidden')",
        f"(contains(@style, 'font-family:') and not({validFonts}))"
    ]:
        for doDel in raw.xpath(f"//*[{delCondition}] | //comment()"):
            doDel.getparent().remove(doDel)
            counter["deleted"] += 1

    # if classdeclaration for hidden
    if cssClasses['hidden']:
        for toDel in raw.xpath(f"//*[@class, {cssClasses['hidden']})]"):
            toDel.getparent().remove(toDel)
            counter["deleted"] += 1

    # refractor images to img
    for image in raw.xpath("//*[local-name()='image']"):
        image.tag = 'img'
        src = image.xpath("./@*[local-name()='href' or local-name()='src']")[0]
        image.attrib.clear()
        image.set('src', src)
        counter["images"] += 1

    for svg in raw.xpath("//*[local-name()='svg']"):
        helper.unwrap(svg)
        counter["deleted"] += 1

    # unwrap child of span and div, that have no text
    for divspan in raw.xpath("//*[local-name()='div' or local-name()='span'][* and not(normalize-space(text()))]"):
        if divspan.get('id', None):
            divspan.getparent().set('id', divspan.get('id', None))
        helper.unwrap(divspan)
        counter["deleted"] += 1

    for divspan in raw.xpath("//*[local-name()='body']/*[local-name()='div' or local-name()='span'][*]"):
        divspan.tag = 'p'
        for child in divspan.xpath(".//*[local-name()='p']"):
            child.tag = 'span'

    # remove everything without text
    #text = text.replace('\u200b', '')  # ZERO WIDTH SPACE
    #text = text.replace('\u200c', '')  # ZERO WIDTH NON-JOINER
    #text = text.replace('\u200d', '')  # ZERO WIDTH JOINER
    #text = text.replace('\ufeff', '')  # ZERO WIDTH NO-BREAK SPACE / BOM
    #"translate(., '\u00A0', ' ')"

    for element in raw.xpath(
        f"//*[not(normalize-space("
        f"translate(., '\u00A0\u200B\u200C\u200D\uFEFF', ' ')"
        f")) and "
        "not(self::*[local-name()='img' or local-name()='hr' or local-name()='link']) and "
        "not(.//*[local-name()='img' or local-name()='hr' or local-name()='link'])]"
    ):
        element.getparent().remove(element)
        counter["deleted"] += 1

    # italic
    for italic in raw.xpath(helper.xpath_for_style_or_classes(
        "font-style:italic",
        cssClasses.get("i", [])
    )):
        helper.wrap(italic, raw, "i")

    # bold
    for bold in raw.xpath(helper.xpath_for_style_or_classes(
        "font-weight:bold",
        cssClasses.get("b", [])
    )):
        helper.wrap(bold, raw, "b")

    # underline
    for underline in raw.xpath(helper.xpath_for_style_or_classes(
        "text-decoration:underline",
        cssClasses.get("u", [])
    )):
        helper.wrap(underline, raw, "u")

    # line-thought
    for linethrough in raw.xpath(helper.xpath_for_style_or_classes(
        "text-decoration:line-through",
        cssClasses.get("s", [])
    )):
        helper.wrap(linethrough, raw, "s")

    # unwrapping all preprocessed stuff
    # span id not taken
    for span in raw.xpath("//*[local-name()='span' and not(parent::*[local-name()='body'])]"):
        if span.get('id', None):
            span.getparent().set('id', span.get('id', None))
        helper.unwrap(span)
        counter["deleted"] += 1

    class_conditions = " or ".join(
        f"contains(@class, '{css_class}')"
        for css_class in cssClasses['center']
    )

    center_xpath = (
        f"//*[contains(@style, 'center') or {class_conditions}]"
    )

    for center in raw.xpath(center_xpath):
        print(center)

    class_conditions = " or ".join(
        f"contains(@class, '{css_class}')"
        for css_class in cssClasses['center']
    )

    center_xpath = (
        f"//*[contains(@style, 'center') or {class_conditions}]"
    )

    for center in raw.xpath(center_xpath):
        print(center)

    # removing attributes
    for element in raw.xpath("//*[@*]"):
        for attr in list(element.attrib):
            if attr.lower() not in ("href", "id", "src"):
                del element.attrib[attr]

    # replacing quote marks with <q></q>
    for element in raw.xpath("//*[local-name()='body']/*"):
        element.getparent().replace(element, quotes(element))

    # first element in body with text => h1
    elements = raw.xpath("//*[local-name()='body']//*[normalize-space(.)]")
    if elements:
        elements[0].tag = 'h1'

    return counter