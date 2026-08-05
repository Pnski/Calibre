from bs4 import BeautifulSoup

def load_chapter(file):
    html = file.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    text = list(BeautifulSoup(html, "lxml-xml").body.stripped_strings)

    return text