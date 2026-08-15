from qt.core import (
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QSizePolicy,
    QHeaderView,
)


class TableWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        db = (
            parent.gui.current_db.new_api
            if hasattr(parent.gui.current_db, "new_api")
            else parent.gui.current_db
        )

        rows = parent.gui.current_view().selectionModel().selectedRows()
        self.book_ids = set(map(parent.gui.library_view.model().id, rows))

        # selection = parent.gui.current_view().selectionModel().selectedRows()
        # model = parent.gui.library_view.model()
        # book_ids = [model.id(index) for index in selection]
        rows = [
            (mi.title, int(db.format_db_size(book_id, "EPUB") / 2**20))
            for book_id in self.book_ids
            for mi in (db.get_metadata(book_id),)
        ]

        # rows = []
        # for book_id in book_ids:
        #    mi = db.get_metadata(book_id)
        #    rows.append([mi.title, int(db.format_db_size(book_id, 'EPUB')/2**20)])

        # print("ID:", book_id)

        # print(db.format_abspath(book_id, 'EPUB'))
        # print(db.format_db_size(book_id, 'EPUB'))

        self.table = QTableWidget(len(rows), 2)
        self.table.setHorizontalHeaderLabels(["Title", "Size [MB]"])

        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(value)))

        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.setSortingEnabled(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
