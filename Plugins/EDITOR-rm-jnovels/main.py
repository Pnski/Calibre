from calibre.gui2.tweak_book.plugin import Tool

from calibre.gui2.tweak_book import current_container
from calibre.ebooks.oeb.polish import toc
from calibre.ebooks.oeb.polish.replace import rationalize_folders, rename_files
from calibre.ebooks.oeb.polish.pretty import pretty_all

from qt.core import QAction

from lxml import etree

import re

patterns = [
    (
        re.compile(r'<!--\s*kobo\b[\s\S]*?</style\s*>', re.IGNORECASE),
        r''
    ),
    (
        re.compile(
            r'<span[^>]*class="koboSpan"[^>]*>(.*?)</span>',
            re.DOTALL
        ),
        r'\1'
    ),
]

class JNovelsRemover(Tool):
    name = "JNovels Remover"
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
        if not self.ensure_book(_('You must first open a book.')):
            return

        self.boss.commit_all_editors_to_container()
        self.boss.add_savepoint('Before: Removing JNovels Ad')

        container = self.current_container  # The book being edited as a container object

        removed = []
        for file in container.manifest_id_map.values():
            if file.lower().endswith('.js') or 'jnovels' in file.lower() or '1.png' in file.lower():
                container.remove_item(file, remove_from_guide=True)
                removed.append(file)

        TYPE_MAP = {
            'text': 'OEBPS/text/',
            'style':'OEBPS/styles/',
            'image':'OEBPS/images/',
            'font':'fonts/',
            'audio':'audio/',
            'video':'video/',
            'opf':'OEBPS/',
            'toc':'OEBPS/',
        }

        rename_map = rationalize_folders(container, TYPE_MAP)
        rename_files(container, rename_map)

        table = toc.get_x_toc(container, toc.find_existing_nav_toc, toc.parse_nav, verify_destinations=False)
        for node in list(table.iterdescendants()):
            if "jnovels" in node.dest.lower():
                toc.remove_names_from_toc(container, [node.dest])

        for file in container.manifest_id_map.values():
            if file.lower().endswith('.xhtml'):
                raw = container.raw_data(file)

                for pattern, replacement in patterns:
                    raw, count = pattern.subn(replacement, raw)

                    if count:
                        print(f"{file}: {count} replacements", flush=True)

                if raw != container.raw_data(file):
                    container.replace(file, etree.fromstring(raw.encode('utf-8')))
        
        pretty_all(container)

        self.boss.show_current_diff()
        self.boss.apply_container_update_to_gui()

    def ensure_book(self, msg=None):
        msg = msg or _('No book is currently open. You must first open a book.')
        if current_container() is None:
            error_dialog(self.gui, _('No book open'), msg, show=True)
            return False
        return True