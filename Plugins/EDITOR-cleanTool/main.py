

from lxml import etree

from qt.core import QAction

from calibre.gui2 import error_dialog
from calibre.gui2.tweak_book.plugin import Tool
from calibre.gui2.tweak_book import current_container
from calibre.ebooks.oeb.polish.replace import rationalize_folders, rename_files
from calibre.ebooks.oeb.polish.pretty import pretty_all

from .body import do_body


import re
CLASS_RE = re.compile(r"\.([_a-zA-Z][\w-]*)")

css_properties = {
    "hidden": ("overflow", "hidden"),
    "center": ("text-align", "center"),
    "right": ("text-align", "right"),
    "i": ("font-style", "italic"),
    "b": ("font-weight", "bold"),
    "u": ("text-decoration", "underline"),
    "s": ("text-decoration", "line-through"),
}

class epubCleaningTool(Tool):
    name = "Cleaning Tool"
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
        for iPath in list(container.name_path_map.keys()):
            if iPath.lower().endswith(font_ext):
                container.remove_item(iPath, remove_from_guide=True)

        TYPE_MAP = {
            "text": "OEBPS/Text/",
            "style": "OEBPS/Styles/",
            "image": "OEBPS/Images/",
            "font": "Fonts/",
            "audio": "Audio/",
            "video": "Video/",
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

        from css_parser.css import CSSRule

        cssClasses = {
            name: set()
            for name in css_properties
        }

        for rule in merged_css.cssRules.rulesOfType(CSSRule.STYLE_RULE):

            for category, (property_name, expected_value) in css_properties.items():
                value = rule.style.getPropertyValue(property_name)

                if value and value.strip().lower() == expected_value:
                    cssClasses[category].update(CLASS_RE.findall(rule.selectorText))

        cssClasses = {
            category: list(classes)
            for category, classes in cssClasses.items()
        }

        print(cssClasses)

        # Process XHTML files
        for file in container.manifest_id_map.values():
            if file.lower().endswith(('.xhtml', '.html')):
                raw = container.parsed(file)

                print(do_body(raw, cssClasses))

                head = raw.xpath('//*[local-name()="head"]')[0]
                etree.strip_elements(head, '{*}link')
                style = raw.makeelement('link', attrib={'href': f'../Styles/{cssFileName}', 'rel': 'stylesheet', 'type': 'text/css'})
                head.append(style)

                container.dirty(file)

        #self.boss.show_current_diff()
        pretty_all(container)
        self.boss.apply_container_update_to_gui(mark_as_modified=True)

    def ensure_book(self, msg=None):
        msg = msg or _("No book is currently open. You must first open a book.")
        if current_container() is None:
            error_dialog(self.gui, _("No book open"), msg, show=True)
            return False
        return True