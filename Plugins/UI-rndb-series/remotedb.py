from urllib.request import Request, urlopen
from email.utils import parsedate_to_datetime

# Static Ranobedb Dump URL for LATEST
DUMP_URL = "https://dumps.ranobedb.org/rndb-db-public-latest.dump.gz"

def download_db(local_file):
    req = Request(DUMP_URL, headers={"User-Agent": "calibre-plugin"})
    with urlopen(req) as response, open(local_file, "wb") as f:
        f.write(response.read())