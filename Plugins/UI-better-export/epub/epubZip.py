# https://manual.calibre-ebook.com/polish.html
# https://github.com/kovidgoyal/calibre/blob/94b9cf8a80930fc61bfc92c7ded08abdb3c224f3/src/calibre/gui2/actions/save_to_disk.py
# https://github.com/kovidgoyal/calibre/blob/94b9cf8a80930fc61bfc92c7ded08abdb3c224f3/src/calibre/gui2/save.py
from calibre.ebooks.oeb.polish.container import get_container as calibre_container
from calibre.library.save_to_disk import config, get_path_components

from pathlib import Path

# from bs4 import BeautifulSoup

from .epubimg import img_mani
from .epubopf import reset_opf_metadata


# this will unpack to local/temp and gives us a wrapper
def epub_container(path, mi, book_id, export_path, prefs):
    # --------------------------------------------------
    # Extract EPUB
    # --------------------------------------------------
    container = calibre_container(path, tweak_mode=True)

    # --------------------------------------------------
    # process EPUB
    # --------------------------------------------------
    if prefs["mod_img"]:
        for key, value in container.mime_map.items():
            if value.lower().startswith("image") and "jnovelclub" not in key.lower():
                img = container.raw_data(key, decode=False, normalize_to_nfc=True)
                r_img = img_mani(img, prefs)
                container.replace(key, r_img)

    # cover
    if prefs["mod_title_img"]:
        cover = get_cover_image(container)
        quality = prefs["mod_img_quality"]
        while container.filesize(cover) > prefs["mod_title_img_max_size"] * 1024:
            img = container.raw_data(cover, decode=False, normalize_to_nfc=True)
            r_img = img_maxsize(img, prefs["mod_title_img_max_size"])
            container.replace(cover, r_img)
            if quality <= 10:
                continue
            else:
                quality -= 1

    if prefs["mod_clean_meta"]:
        reset_opf_metadata(container)

    # --------------------------------------------------
    # Write processed EPUB
    # --------------------------------------------------

    components = get_path_components(
        config().parse(),
        mi,
        book_id,
        1024,  # max name length
    )

    base_path = Path(export_path).joinpath(*components)
    epub_path = base_path.with_suffix(".epub")

    epub_path.parent.mkdir(parents=True, exist_ok=True)

    container.commit(str(epub_path))


# chatgpt, has to be tested till crash
def get_cover_image(container):
    cover_page = container.guide_type_map.get("cover")
    if not cover_page:
        return None

    root = container.parsed(cover_page)

    # 1) HTML <img src="...">
    src = root.xpath('//*[local-name()="img"]/@src')
    if src:
        return container.href_to_name(src[0], cover_page)

    # 2) SVG <image ... href="..."> (sometimes plain href)
    href = root.xpath('//*[local-name()="image"]/@href')
    if href:
        return container.href_to_name(href[0], cover_page)

    # 3) SVG <image ... xlink:href="..."> (your sample)
    xlink_href = root.xpath(
        '//*[local-name()="image"]/@*[local-name()="href" and namespace-uri()="http://www.w3.org/1999/xlink"]'
    )
    if xlink_href:
        return container.href_to_name(xlink_href[0], cover_page)

    # 4) Fallback: any attribute whose local-name is "href" or "src" on an <image>
    any_href = root.xpath(
        '//*[local-name()="image"]/@*[local-name()="href" or local-name()="src"]'
    )
    if any_href:
        return container.href_to_name(any_href[0], cover_page)

    return None
