from . import helper

def attributes(element, raw, css):
    child_removed = False

    # Use list() because children may be removed during recursion
    for child in list(element):
        if attributes(child, raw, css):
            child_removed = True

    style = get_combined_style(element, css)

    valid_fonts = [
        None,
        "serif",
        "sans-serif",
        "monospace",
        "times new roman",
        "arial",
    ]

    if style.get('overflow') == 'hidden' or style.get('font-family') not in valid_fonts:
        #print(element, element.tag)
        element.getparent().remove(element)
        return True

    element_id = element.attrib.get('id')
    href = element.attrib.get('href')

    element.attrib.clear()

    if href is not None:
        element.set("href", href)

    if element_id is not None:
        element.set("id", element_id)

    if style.get("text-align") == "center":
        element.set("class", "center")
    elif style.get("text-align") == "right":
        element.set("class", "right")

    if style.get("font-weight") == "bold":
        helper.wrap(element, raw, "b")

    if style.get("font-style") == "italic":
        helper.wrap(element, raw, "i")

    if "underline" in style.get("text-decoration", ""):
        helper.wrap(element, raw, "u")

    if "line-through" in style.get("text-decoration", ""):
        helper.wrap(element, raw, "s")

    return child_removed


#import css_parser
from css_parser import parseStyle

def get_combined_style(element, css):
    styles = {}

    # CSS from classes
    classes = (element.get("class") or "").split()

    for class_name in classes:
        selector = "." + class_name

        for rule in css.cssRules:
            selector_text = getattr(rule, "selectorText", None)

            if not selector_text:
                continue

            selectors = [
                s.strip()
                for s in selector_text.split(",")
                if s.strip()
            ]

            if selector in selectors:
                for property in rule.style:
                    styles[property.name] = property.value

    # Inline style overrides class style
    inline_style = element.get("style")
    if inline_style:
        inline = parseStyle(inline_style)

        for property in inline:
            styles[property.name] = property.value

    return styles