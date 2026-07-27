from calibre.gui2.actions import InterfaceAction

from qt.core import (
    QDialog,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
)

from calibre.utils.date import parse_date

from .localdb import (
    check_local,
    #find_rows,
    # find_rows_fuzzy,
    # get_book_by_id,
    get_book_series_release,
    get_mi_by_rndbid,
    get_mi_by_title_sorted,
)
from .parser import (
    _parse_date,
    parse_book_number,
)

class InterfacePlugin(InterfaceAction):

    name = 'Check RNDB Series'

    action_spec = (name, None, 'Check for new books in Series', ())

    def genesis(self):
        icon = get_icons('images/icon.png', self.name)

        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_table)

    def show_table(self):
        # init calibre db
        db = self.gui.current_db.new_api if hasattr(self.gui.current_db, 'new_api') else self.gui.current_db
        
        #init or update local db
        check_local(7) #fix static days

        view = self.gui.library_view.model()
        book_ids = view.all_current_book_ids()
        #print(view)
        #print(book_ids)

        series = []
        rndb_ids = []

        for book_id in book_ids:
            serie = db.field_for('series', book_id)
            if not serie:
                continue
            series.append(serie)

            identifiers = db.field_for('identifiers', book_id) or {}
            rndb_id = identifiers.get("ranobedb")
            if not rndb_id:
                continue
            rndb_ids.append(rndb_id)

            #series.setdefault(serie, []).append(str(rndb_id))
        
        rows = []
        #for serie, series_rndbids in series.items():
        #    for book in get_book_series_release(serie,series_rndbids):
        #        rows.append((serie,book[0],book[1]))
        for book in get_book_series_release(series,rndb_ids):
            rows.append((book[0],book[1],book[2]))
        """ rows = []

        for serie in db.all_field_names('series'):
            
            books_in_series = db.get_next_series_num_for(serie, field='series', current_indices=True) #int
            series_rndbids = []
            
            for calibre_id in db.get_next_series_num_for(serie, field='series', current_indices=True).keys():
                rndb_ident = db.get_metadata(calibre_id).identifiers.get("ranobedb")
                if rndb_ident:
                    series_rndbids.append(str(rndb_ident))
            for k in get_book_series_release(serie,series_rndbids):
                rows.append((serie,k[0],k[1])) """

        dialog = QDialog(self.gui)
        dialog.setWindowTitle("RNDB Series Checker")
        dialog.resize(800, 400)

        layout = QVBoxLayout(dialog)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Series Title", "Series Book", "Release Date"])

        self.table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(str(value)))

        self.table.horizontalHeader().setStretchLastSection(True)

        width = self.table.viewport().width()

        self.table.setColumnWidth(0, int(width * 0.45))
        self.table.setColumnWidth(1, int(width * 0.45))
        self.table.setColumnWidth(2, int(width * 0.1))

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.itemDoubleClicked.connect(self.search_series)

        self.table.setSortingEnabled(True)   

        dialog.setModal(False)
        dialog.show()

        # Keep a reference so it isn't garbage collected
        self.dialog = dialog

    def search_series(self, item):
        #table = self.sender()
        series = self.table.item(item.row(), 0).text()

        self.gui.search.set_search_string(f'{series}')
        self.gui.search.do_search()