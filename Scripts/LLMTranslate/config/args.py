#   ############################################
#
#   Argumentparser
#
#   ############################################

import argparse


parser = argparse.ArgumentParser(
    prog='start.py',
    description='This tool is designed to fully translate an epub form JA/CN/KR to EN',
    #epilog='Text at the bottom of help'
)
parser.add_argument('-p','--path',nargs=1,help='Absolute path of the epub')
parser.add_argument('-op',help='Open a Path Dialog',action='store_true')
parser.add_argument('-c','--cache',nargs=1,help='Optional cache folder, by default it is the root of this project')
parser.add_argument('-v', '--verbose', action='store_true')  # on/off flag

args = parser.parse_args()

#   ############################################
#
#   tomllibs
#
#   ############################################

import tomllib

with open("config/prompts.toml", "rb") as f:
    prompts = tomllib.load(f)

with open("config/base.toml","rb") as f:
    base = tomllib.load(f)

#   ############################################
#
#   logging
#
#   ############################################
import logging

class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[41m",
    }
    RESET = "\033[0m"

    def format(self, record):
        original = record.levelname
        color = self.COLORS.get(record.levelno, "")
        record.levelname = f"{color}{original}{self.RESET}"
        try:
            return super().format(record)
        finally:
            record.levelname = original

fmt = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"

handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter(fmt, datefmt="%H:%M:%S"))

logging.basicConfig(
    level=logging.DEBUG if args.verbose else logging.INFO,
    handlers=[handler],
    #force=True,  # overwrites existing basicConfig in many environments
)