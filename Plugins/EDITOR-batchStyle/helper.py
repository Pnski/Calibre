def wrap(element, tree, tag):
    wrapper = tree.makeelement(tag)

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

    for child in list(element):
        parent.insert(index, child)
        index += 1

    if element.text:
        if index == 0:
            parent.text = (parent.text or "") + element.text
        else:
            previous = parent[index - 1]
            previous.tail = (previous.tail or "") + element.text

    if element.tail:
        if index == 0:
            parent.text = (parent.text or "") + element.tail
        else:
            previous = parent[index - 1]
            previous.tail = (previous.tail or "") + element.tail

    parent.remove(element)

def ln(element):
    return element.tag.rsplit('}', 1)[-1].lower()