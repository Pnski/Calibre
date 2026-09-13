import base64

from calibre.gui2.tweak_book import current_container
from calibre.gui2.tweak_book.plugin import Tool
from qt.core import (
    QAction,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)


class addWM(Tool):
    name = "Add Watermarks"
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

        dialog = InputDia(self.gui)

        if dialog.exec() != QDialog.Accepted:
            return None

        dialogData = dialog.get_values()

        self.boss.commit_all_editors_to_container()
        self.boss.add_savepoint("Before: Adding Watermarks")

        container = (
            self.current_container
        )  # The book being edited as a container object

        if not dialogData.get("text") or len(dialogData.get("text")) == 0:
            return

        if dialogData.get("base64"):
            dialogData["text"] = base64.b64encode(dialogData.get("text").encode("utf-8")).decode("ascii")


        if dialogData.get("jpg"):
            for iPath in container.name_path_map.keys():
                if iPath.lower().endswith(("jpg", "jpeg")):
                    img = container.parsed(iPath)  # binary
                    img += dialogData.get("text").encode("utf-8")
                    container.replace(iPath, img)

        if dialogData.get("cssComment"):
            from css_parser.css import CSSComment
            for file in container.manifest_items_of_type(["text/css"]):
                parsed = container.parsed(file)
                parsed.add(CSSComment(f"/* {dialogData.get("text")} */"))
                container.dirty(file)

        if dialogData.get("headerComment"):
            from lxml import etree
            for file in container.manifest_id_map.values():
                if file.lower().endswith("html"):
                    raw = container.parsed(file)
                    for header in raw.xpath("//*[local-name()='head']"):
                        comment = etree.Comment(dialogData.get("text"))
                        header.append(comment)

                    container.dirty(file)
        
        if dialogData.get("metaData"):
            for meta in container.opf.xpath("//*[local-name()='metadata']"):
                    data = etree.Element("meta")
                    data.set("property", "WaterMark")
                    data.text = dialogData.get("text")
                    meta.append(data)
            container.dirty(container.opf_name)

        if dialogData.get("bodyData"):
            from lxml import etree
            for file in container.manifest_id_map.values():
                if file.lower().endswith("html"):
                    raw = container.parsed(file)
                    for body in raw.xpath("//*[local-name()='body']"):
                        body.set("data-WaterMark", dialogData.get("text"))

                    container.dirty(file)
      
        self.boss.show_current_diff()
        self.boss.apply_container_update_to_gui()

    def ensure_book(self, msg=None):
        msg = msg or _("No book is currently open. You must first open a book.")
        if current_container() is None:
            error_dialog(self.gui, _("No book open"), msg, show=True)
            return False
        return True


class InputDia(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Insert metadata")

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.text = QLineEdit()
        form.addRow("Text:", self.text)

        self.base64 = QCheckBox("Base 64 Encrypted Message?")
        self.jpg = QCheckBox("JPG")
        self.cssComment = QCheckBox("Css Comment")
        self.headerComment = QCheckBox("Header Comment")
        self.meta = QCheckBox("Metadata field")
        self.bodyData = QCheckBox("Body Data Field")

        for CheckBox in [
            self.base64,
            self.jpg,
            self.cssComment,
            self.headerComment,
            self.meta,
            self.bodyData,
        ]:
            form.addRow(CheckBox)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def get_values(self):

        return {
            "text": self.text.text(),
            "base64": self.base64.isChecked(),
            "jpg": self.jpg.isChecked(),
            "cssComment": self.cssComment.isChecked(),
            "headerComment": self.headerComment.isChecked(),
            "metaData": self.meta.isChecked(),
            "bodyData": self.bodyData.isChecked(),
        }
