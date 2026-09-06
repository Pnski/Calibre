from calibre.gui2.tweak_book.plugin import Tool

from calibre.gui2.tweak_book import current_container
from calibre.ebooks.oeb.polish.toc import get_x_toc, find_existing_ncx_toc, parse_ncx, find_existing_nav_toc, parse_nav, remove_names_from_toc
from calibre.ebooks.oeb.polish.replace import rationalize_folders, rename_files
from calibre.ebooks.oeb.polish.pretty import pretty_all

from qt.core import QAction, QMessageBox

from . import helper

import base64
from html import escape

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

        self.boss.add_savepoint('After: Rationalize Folders')

        container = self.current_container

        removedMeta = []
        for doDel in container.opf.xpath("//*[local-name()='meta' and (contains(@name,'JNC') or contains(@name,'Sigil'))]"):
            removedMeta.append(doDel.attrib)
            doDel.getparent().remove(doDel)
            container.dirty(container.opf_name)

        removedFiles = []
        #name_path_map reveals ALL files in the epub
        for iPath in list(container.name_path_map.keys()):
            if iPath.lower().endswith('js') or any(term in iPath.lower() for term in ("jnovels", "1.png", "rights.xml", "calibre")):
                container.remove_item(iPath, remove_from_guide=True)
                removedFiles.append(iPath)

        removedComments = 0
        for file in container.manifest_items_of_type(['text/css']):
            parsed = container.parsed(file)
            for index, rule in enumerate(parsed):
                if rule.type == 1001: #comment
                    parsed.deleteRule(index)
                    container.dirty(file) #flag
                    removedComments += 1

        removedToc = 0
        #remove jnovels from all EPUB-TOC
        for tocTable in [get_x_toc(container, find_existing_ncx_toc, parse_ncx, verify_destinations=False), get_x_toc(container, find_existing_nav_toc, parse_nav, verify_destinations=False)]:
            for tocIndex in list(tocTable.iterdescendants()):
                if "jnovels" in tocIndex.dest.lower():
                    remove_names_from_toc(container, [tocIndex.dest])
                    removedToc += 1

        removedKobo = 0
        for file in container.manifest_id_map.values():
            if file.lower().endswith('html'):
                raw = container.parsed(file)

                for style in raw.xpath("//*[local-name()='span' and @class='koboSpan']"):
                    helper.unwrap(style)
                    removedKobo += 1

                for doDel in raw.xpath("//*[local-name()='style' or local-name()='script'] | //comment()"):
                    doDel.getparent().remove(doDel)
                    removedKobo += 1

                container.dirty(file)

        imgData = []
        # PIL seem to be the wrong choice since it removes more infos?
        for iPath in container.name_path_map.keys():
            if iPath.lower().endswith(('jpg', 'jpeg')):
                img = container.parsed(iPath)#binary

                #reversefind
                end_marker = img.rfind(b"\xff\xd9")#binary ffd9 is jpg marker

                if end_marker == -1 or end_marker == len(img)-2: #errorhandling
                    print(f"No Extra Info ({end_marker+2}/{len(img)}): {iPath}")
                else:
                    imgData.append(img[end_marker + 2:].hex())
                    container.replace(iPath, img[:end_marker + 2])
                    #container.dirty(iPath)
            elif iPath.lower().endswith('png'):
                img = container.parsed(iPath)

                assert img[:8] == b'\x89PNG\r\n\x1a\n', 'Png is not a PNG!'

                imgLength = len(img)
                pos = 8
                png = bytearray(b'\x89PNG\r\n\x1a\n')

                while pos +8 < len(img):
                    #chunk_len = int.from_bytes(img[pos:pos+4], 'big')
                    chunk_type = img[pos+4:pos+8]
                    chunk_end = pos + 8 + int.from_bytes(img[pos:pos+4], 'big') + 4  # +4 crc

                    if chunk_end > len(img):
                        break

                    chunk = img[pos:chunk_end]
                    if chunk_type in {b'IHDR', b'PLTE', b'tRNS', b'IDAT', b'IEND'}:
                        #print('keep',chunk)
                        png.extend(chunk)
                    else:
                        data = chunk.decode("utf-8", errors="replace")
                        print(data)
                        imgData.append(data)
                    pos = chunk_end
                    if chunk_type == b'IEND':
                        break
                
                container.replace(iPath, png)
        QMessageBox.information(
            None,
            "Info",
            f"""
            <table>
                <tr>
                    <td>Files removed:</td><td>{"\n".join(removedFiles)}</td>
                </tr><tr>
                    <td>Meta removed:</td><td>{removedMeta}</td>
                </tr><tr>
                    <td>RemovedCss:</td><td>{removedComments}</td>
                </tr><tr>
                    <td>TOC removed:</td><td>{removedToc}</td>
                </tr><tr>
                    <td>Kobo entrys removed:</td><td>{removedKobo}</td>
                </tr><tr>
                    <td>Image data cleaned:</td><td style="white-space: pre-wrap; overflow-wrap: anywhere;">{escape("".join(list(dict.fromkeys(imgData))))}</td>
                </tr>
            </table>
            """
        )

        pretty_all(container)

        self.boss.show_current_diff()
        self.boss.apply_container_update_to_gui()

    def ensure_book(self, msg=None):
        msg = msg or _('No book is currently open. You must first open a book.')
        if current_container() is None:
            error_dialog(self.gui, _('No book open'), msg, show=True)
            return False
        return True