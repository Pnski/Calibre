from lxml import etree

def reset_opf_metadata(container):    
    # Find the <metadata> node
    meta_nodes = container.opf_xpath("//*[local-name()='metadata']")
    #meta_nodes = container.opf_xpath("//opf:metadata")
    if not meta_nodes:
        return

    keep = ["title", "creator"]

    for child in list(meta_nodes[0]):
        if etree.QName(getattr(child, "tag", None)).localname.lower() not in keep and (child.get("name") or "").lower() != "cover":
            meta_nodes[0].remove(child)
