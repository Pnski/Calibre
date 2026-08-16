from pathlib import Path

from qt.core import (
    QDialog,
    QGridLayout,
    QLabel,
    QDialogButtonBox,
    QPushButton,
    QLineEdit,
    QFileDialog,
    Qt,
    QSizePolicy,
)

from .config import ConfigWidget
from .table import TableWidget

from ..epub.epubZip import epub_container


class Dialog(QDialog):
    def __init__(self, gui, icon):
        QDialog.__init__(self, gui)
        self.gui = gui

        layout = QGridLayout(self)

        # layout.addWidget(widget, row, column, rowSpan, columnSpan, alignment)

        self.config = ConfigWidget(self)
        layout.addWidget(self.config, 1, 1, 1, 2)

        d_folder = QLineEdit("Select a folder.")
        d_folder_btn = QPushButton("Open folder")
        # print(QFileDialog.getExistingDirectory(self, "Select a directory", d_folder.text()))

        d_folder_btn.clicked.connect(
            lambda: d_folder.setText(
                QFileDialog.getExistingDirectory(
                    self, "Select a directory", d_folder.text()
                )
            )
        )

        layout.addWidget(d_folder, 2, 1, 1, 1, Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(d_folder_btn, 2, 2, 1, 1, Qt.AlignmentFlag.AlignBottom)

        self.table = TableWidget(self)
        layout.addWidget(self.table, 1, 3, 1, 2)

        process = QPushButton("Process Files")
        process.clicked.connect(lambda: self.process_files(d_folder.text()))

        layout.addWidget(process, 2, 3, 1, 1)

        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(2, 0)

        layout.setColumnStretch(3, 1)
        layout.setColumnStretch(4, 1)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 0)

        self.setLayout(layout)
        self.resize(800, 800)

    def process_files(self, path):
        db = (
            self.gui.current_db.new_api
            if hasattr(self.gui.current_db, "new_api")
            else self.gui.current_db
        )

        from calibre.gui2 import Dispatcher

        # gui.job_manager.run_job(Dispatcher(job_done), 'arbitrary',
        #    args=('calibre_plugins.myplugin.worker', 'do_work',
        #            ('arg1' 'arg2', 'arg3')),
        #            description='Change the world')

        def job_done(result):
            print("done:", result)
    
        for book_id in self.table.book_ids:
            self.gui.job_manager.run_job(
                Dispatcher(job_done),
                "arbitrary",
                args=(
                    "calibre_plugins.better_export.epub.epubZip",
                    "epub_container",
                    (
                        db.format_abspath(book_id, "EPUB"),
                        book_id,
                        path,
                        {
                            **self.config.prefs.defaults,
                            **dict(self.config.prefs),
                        }
                    ),
                ),
                description="Converting and Exporting EPUBS",
            )