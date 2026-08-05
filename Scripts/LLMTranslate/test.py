from bs4 import BeautifulSoup
from pathlib import Path

def load_chapter(file):
    html = file.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    text = list(BeautifulSoup(html, "lxml-xml").body.stripped_strings)

    return text

print(load_chapter(Path(r"cache\父は英雄、母は精霊、娘の私は転生者。 ８ (カドカワBOOKS)\text\part0000.html")))
print(load_chapter(Path(r"cache\父は英雄、母は精霊、娘の私は転生者。 ８ (カドカワBOOKS)\text\part0008.html")))