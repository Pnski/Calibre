def wrap(element, raw, tag):
    wrapper = raw.makeelement(tag)

    wrapper.text = element.text
    element.text = None

    for child in list(element):
        element.remove(child)
        wrapper.append(child)

    element.append(wrapper)

def unwrap(element):
    parent = element.getparent()

    if parent is None:
        return

    index = parent.index(element)
    children = list(element)

    # Text before the first child must be inserted at the original position
    if element.text:
        if index == 0:
            parent.text = (parent.text or "") + element.text
        else:
            previous = parent[index - 1]
            previous.tail = (previous.tail or "") + element.text

    # Move the children into the element's position
    for offset, child in enumerate(children):
        parent.insert(index + offset, child)

    # Text after the unwrapped element belongs after its last child
    if element.tail:
        if children:
            last_child = children[-1]
            last_child.tail = (last_child.tail or "") + element.tail
        elif index == 0:
            parent.text = (parent.text or "") + element.tail
        else:
            previous = parent[index - 1]
            previous.tail = (previous.tail or "") + element.tail

    parent.remove(element)


def ln(element):
    return element.tag.rsplit('}', 1)[-1].lower()

def xpath_for_style_or_classes(style_text, class_names):
    conditions = [
        f"contains(translate(@style, ' ', ''), '{style_text}')"
    ]

    # font-weight:bold should also match 600-900
    if style_text == "font-weight:bold":
        conditions.extend([
            "contains(translate(@style, ' ', ''), 'font-weight:600')",
            "contains(translate(@style, ' ', ''), 'font-weight:700')",
            "contains(translate(@style, ' ', ''), 'font-weight:800')",
            "contains(translate(@style, ' ', ''), 'font-weight:900')",
        ])

    if isinstance(class_names, str):
        class_names = [class_names]

    for class_name in class_names or []:
        if class_name:
            conditions.append(
                "contains(concat(' ', normalize-space(@class), ' '), "
                f"' {class_name} ')"
            )

    return "//*[" + " or ".join(conditions) + "]"

def alignment(raw, cssClasses, alignment):
    conditions = [
        f"contains(@style, '{alignment}')"
    ]

    conditions.extend(
        f"contains(@class, '{css_class}')"
        for css_class in cssClasses.get(alignment, [])
    )

    xpath = f"//*[{ ' or '.join(conditions) }]"

    for element in raw.xpath(xpath):
        keep = {
            'id': element.get('id'),
            'href': element.get('href'),
            'src': element.get('src'),
        }

        element.attrib.clear()

        element.set('class', alignment)

        for key, value in keep.items():
            if value is not None:
                element.set(key, value)