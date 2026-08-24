import re

from lxml import etree

import css_parser

from qt.core import QAction

from calibre.gui2 import error_dialog
from calibre.gui2.tweak_book.plugin import Tool
from calibre.gui2.tweak_book import current_container
from calibre.ebooks.oeb.polish.replace import rationalize_folders, rename_files
from calibre.ebooks.oeb.polish.pretty import pretty_all

# CG scrapeprot -> vocal
# footnotes
# static text duplicator detector
# duplicate detector

class Remover(Tool):
    name = "Remover"
    allowed_in_toolbar = True
    allowed_in_menu = True
    default_shortcut = ()

    def create_action(self, for_toolbar=True):
        ac = QAction(get_icons("images/icon.png"), self.name, self.gui)
        if not for_toolbar:
            self.register_shortcut(ac, self.name, default_keys=self.default_shortcut)
        ac.triggered.connect(self.clean)
        return ac

    def clean(self):
        if not self.ensure_book(_("You must first open a book.")):
            return

        self.boss.add_savepoint("Before: Automatic Changes")

        container = self.current_container

        font_ext = ('.ttf', '.otf', '.woff', '.woff2')
        for file_path in list(container.manifest_id_map.values()):
            if file_path.lower().endswith(font_ext):
                container.remove_item(file_path, remove_from_guide=True)

        TYPE_MAP = {
            "text": "OEBPS/text/",
            "style": "OEBPS/styles/",
            "image": "OEBPS/images/",
            "font": "fonts/",
            "audio": "audio/",
            "video": "video/",
            "opf": "OEBPS/",
            "toc": "OEBPS/",
        }

        merged_css = None
        for file in container.manifest_items_of_type(['text/css']):
            parsed = container.parsed(file)

            if merged_css is None:
                merged_css = parsed
            else:
                # Append rules from subsequent stylesheets into the first stylesheet
                for rule in parsed.cssRules:
                    merged_css.cssRules.append(rule)

            container.remove_item(file, remove_from_guide=True)

        from .stylesheet import CSS

        cssFileName = "nyk.css"

        container.add_file(
            name=cssFileName,
            data=CSS.encode("utf-8")
        )

        rename_map = rationalize_folders(container, TYPE_MAP)
        rename_files(container, rename_map)

        self.boss.add_savepoint("SAVEPOINT FOLDER")
        container = self.current_container
        
        # Process XHTML files
        for file in container.manifest_id_map.values():
            if file.lower().endswith(('.xhtml', '.html')):
                raw = container.parsed(file)

                for c in raw.xpath('//comment()'):
                    c.getparent().remove(c)

                body = raw.xpath("//*[local-name()='body']")[0]
                index = 0

                while index < len(body):
                    element = body[index]

                    tag = element.tag.rsplit('}', 1)[-1].lower()

                    if tag in ('div', 'span', 'svg'):
                        unwrap_element(element)
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

                    # del button
                    if tag == 'br':
                        body.remove(element)
                        continue

                    if tag in ('img', 'a'):
                        #print("element img skipping", element)
                        index += 1
                        continue

                    if not ''.join(element.itertext()).strip():
                        if element.xpath('.//*[local-name()="img" or local-name()="image"]'):
                            unwrap_element(element)
                            continue
                        else:
                            body.remove(element)
                            continue

                    attributes(element, raw, merged_css)
                    etree.strip_tags(element, '{*}span')

                    replacement = replace_quotes(element)
                    body[index] = replacement
                    index += 1

                # First Element = h1 if not img
                element = body[0]
                tag = element.tag.rsplit('}', 1)[-1].lower()
                if tag not in ('img', 'a'):
                    element.tag = 'h1'

                container.dirty(file)

        for file in container.manifest_id_map.values():
            if file.lower().endswith(('.xhtml', '.html')):
                raw = container.parsed(file)
                head = raw.xpath('//*[local-name()="head"]')[0]
                etree.strip_tags(head, '{*}link')
                style = raw.makeelement('link')
                style.set('href',f'../styles/{cssFileName}')
                style.set('rel','stylesheet')
                style.set('type','text/css')
                head.append(style)

        #self.boss.show_current_diff()
        pretty_all(container)
        self.boss.apply_container_update_to_gui(mark_as_modified=True)

    def ensure_book(self, msg=None):
        msg = msg or _("No book is currently open. You must first open a book.")
        if current_container() is None:
            error_dialog(self.gui, _("No book open"), msg, show=True)
            return False
        return True

def local_name(element):
    return element.tag.rsplit('}', 1)[-1].lower()


def attributes(element, raw, css):
    for child in element:
        attributes(child, raw, css) #recursion

    style = get_combined_style(element, css)

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
        wrap_contents(element, raw, "b")

    if style.get("font-style") == "italic":
        wrap_contents(element, raw, "i")

    if "underline" in style.get("text-decoration", ""):
        wrap_contents(element, raw, "u")

    if "line-through" in style.get("text-decoration", ""):
        wrap_contents(element, raw, "s")

def get_combined_style(element, merged_css):
    styles = {}

    # CSS from classes
    classes = (element.get("class") or "").split()

    for class_name in classes:
        selector = "." + class_name

        for rule in merged_css.cssRules:
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
        inline = css_parser.parseStyle(inline_style)

        for property in inline:
            styles[property.name] = property.value

    return styles

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

# 1. Match quote pairs using [^<>]*? so contents cannot cross < or >
pair_patterns = [
    f"{re.escape(o)}([^<>]*?){re.escape(c)}" for o, c in QUOTE_PAIRS.items()
]
combined_quotes = "|".join(pair_patterns)

# 2. Group 1 matches HTML tags (<...>); Group 2 matches Quote Pairs outside tags
TAG_OR_QUOTE_REGEX = re.compile(rf'(<[^>]+>)|({combined_quotes})', re.DOTALL)


def replace_quotes(p):
    #new stuff from chatgpt
    text = etree.tostring(p, encoding='unicode', with_tail=False)

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
        return etree.fromstring(text.encode('utf-8'))
    except etree.XMLSyntaxError:
        print(text)
        raise

def wrap_contents(element, tree, tag):
    wrapper = tree.makeelement(tag)

    wrapper.text = element.text
    element.text = None

    for child in list(element):
        element.remove(child)
        wrapper.append(child)

    element.append(wrapper)

def unwrap_element(element):
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