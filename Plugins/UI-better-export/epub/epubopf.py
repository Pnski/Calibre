from lxml import etree


def reset_opf_metadata(container):
    # Find the <opf:metadata> node
    meta_nodes = container.opf_xpath("//opf:metadata")
    if not meta_nodes:
        return

    keep = ["title", "creator"]

    for child in list(meta_nodes[0]):
        if etree.QName(child).localname.lower() not in keep:
            meta_nodes[0].remove(child)
