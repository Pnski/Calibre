import logging
logger = logging.getLogger(__name__)

import shutil
import zipfile
from pathlib import Path

from config.args import args


def extract(epub_path: str) -> Path:

    logger.debug("==========================")
    logger.debug("EPUB extraction")
    logger.debug("==========================")

    epub = Path(epub_path).resolve()

    if not epub.exists():
        raise FileNotFoundError(epub)

    if epub.suffix.lower() != ".epub":
        raise ValueError(f"{epub} is not an EPUB file.")

    project_root = Path.cwd()

    cache_root = project_root / "cache"
    logger.debug('Cache Dir:',cache_root)
    cache_root.mkdir(exist_ok=True)

    extract_folder = cache_root / epub.stem

    if extract_folder.exists():
        shutil.rmtree(extract_folder)

    extract_folder.mkdir()

    with zipfile.ZipFile(epub, "r") as zf:
        logger.debug("Extracting:", zf.namelist())
        zf.extractall(extract_folder)

    logger.debug("Finished Extraction")

    return extract_folder