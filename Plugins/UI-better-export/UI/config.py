from calibre.utils.config import JSONConfig

from qt.core import (
    QWidget,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QCheckBox,
    QSpinBox,
    QHeaderView,
    Qt,
)

prefs = JSONConfig("plugins/better_export")

prefs.defaults.update(
    {
        "mod_img": True,
        "mod_img_quality": 95,
        "mod_img_size_dimension": True,
        "mod_img_size_dimension.width": 1072,
        "mod_img_size_dimension.height": 1448,
        "mod_img_grsc": True,
        "mod_img_rota": True,
        # Title Image
        "mod_title_img": True,
        "mod_title_img_max_size": 1024,
        # Metadata
        "mod_clean_meta": True,
        # Copyright
        # "mod_del_copyright": True,
        # clean BS
        "proofread": True,
    }
)


class ConfigWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)

        self.tree.setHeaderLabels(["Category", "Value"])

        images = QTreeWidgetItem(self.tree, ["Images", ""])
        images.setData(0, Qt.ItemDataRole.UserRole, "mod_img")
        images.setExpanded(prefs["mod_img"])

        self.add_spinbox(images, "Image Quality:", "mod_img_quality", 10, 100)

        dimensions = QTreeWidgetItem(images, ["Dimension", ""])
        dimensions.setData(0, Qt.ItemDataRole.UserRole, "mod_img_size_dimension")
        dimensions.setExpanded(prefs["mod_img_size_dimension"])

        self.add_spinbox(
            dimensions, "Max Width:", "mod_img_size_dimension.width", 0, 5000
        )
        self.add_spinbox(
            dimensions, "Max Height:", "mod_img_size_dimension.height", 0, 5000
        )

        self.add_checkbox(images, "Convert images to grayscale", "mod_img_grsc")

        _rotate = self.add_checkbox(images, "Rotate big images", "mod_img_rota")
        _rotate.setToolTip("Rotate big images (>400x400) -90°")

        title_image = QTreeWidgetItem(self.tree, ["Title Image", ""])
        title_image.setData(0, Qt.ItemDataRole.UserRole, "mod_title_img")
        title_image.setExpanded(prefs["mod_title_img"])

        self.add_spinbox(
            title_image, "Max Size in KB:", "mod_title_img_max_size", 500, 9999
        )

        self.add_checkbox(self.tree, "RM Metadata", "mod_clean_meta")

        # meta = QTreeWidgetItem(self.tree, ["Metadata", ""])
        # meta.setExpanded(True)

        # copyr = QTreeWidgetItem(self.tree, ["Delete Copyright Pages", ""])
        # copyr.setExpanded(True)

        proofread = QTreeWidgetItem(self.tree, ["Proofread", ""])
        # guten hinweis, was wird überhaupt geändert
        # abkürzungen?
        proofread.setExpanded(True)

        hdr = self.tree.header()
        hdr.setStretchLastSection(False)
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        layout = QVBoxLayout(self)

        self.prefs = prefs

        self.tree.itemExpanded.connect(self.on_item_expanded)
        self.tree.itemCollapsed.connect(self.on_item_collapsed)

        layout.addWidget(self.tree)

    def add_checkbox(self, parent, label, setting):
        item = QTreeWidgetItem(parent, [label, ""])

        checkbox = QCheckBox()
        checkbox.setChecked(prefs[setting])

        checkbox.stateChanged.connect(
            lambda state: self.on_state_changed(setting, state)
        )

        self.tree.setItemWidget(item, 1, checkbox)

        return checkbox

    def add_spinbox(self, parent, label, setting, minimum, maximum):
        item = QTreeWidgetItem(parent, [label, ""])

        spinbox = QSpinBox()
        spinbox.setRange(minimum, maximum)
        spinbox.setValue(prefs[setting])

        spinbox.valueChanged.connect(
            lambda value: self.on_value_changed(setting, value)
        )

        self.tree.setItemWidget(item, 1, spinbox)

        return spinbox

    def on_state_changed(self, setting, state):
        prefs[setting] = state != 0

    def on_value_changed(self, setting, value):
        prefs[setting] = value

    def on_item_expanded(self, item):
        setting = item.data(0, Qt.ItemDataRole.UserRole)
        print(setting, item)

        if setting:
            prefs[setting] = True

    def on_item_collapsed(self, item):
        setting = item.data(0, Qt.ItemDataRole.UserRole)
        print(setting, item)

        if setting:
            prefs[setting] = False
