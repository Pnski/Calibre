

import sys

from pathlib import Path

from config.args import args
import logging
logger = logging.getLogger(__name__)

from epub.extract import extract
from phases.p1.scene_planner import scene_planner

#from epub_extract import extract_epub
#from epub_p1_ingest import run_p1

""" import threading

def load_in_background():
    global heavy_module
    import heavy_module
    heavy_module = heavy_module

t = threading.Thread(target=load_in_background, daemon=True)
t.start() """



#   ############################################
#
#
#
#   ############################################

def main():
    if args.op:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()  # hide the main window

        path = filedialog.askopenfilename(
            title="Select input file",
            filetypes=[("All files", "*.*")]
        )

        root.destroy()

        if not path:
            logger.critical("Error: No input selected. ABORTING")
            raise SystemExit(1)
        else:
            args.path = path

    if args.path is None:
        logger.critical("Error in pathing ABORT")
        raise SystemExit(1)

    book_folder = extract(
        args.path
    )

    scene_planner(
        book_folder
    )


    return 0

if __name__ == "__main__":
    sys.exit(main())