import logging
logger = logging.getLogger(__name__)

from config.args import args, base

def write_content(folder, phase, filename, content):
    oFolder = (folder / phase)
    oFolder.mkdir(parents=True, exist_ok=True)

    oFile = (oFolder / filename.with_suffix(base[phase]['file_extension']).name)

    oFile.write_text(content,encoding="utf-8")

    logger.debug(f"Saved: {oFile}")