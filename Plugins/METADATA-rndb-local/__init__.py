from calibre.ebooks.metadata.sources.base import Option, Source

import re
from functools import partial

from .localdb import (
    check_local,
    find_rows,
    # find_rows_fuzzy,
    # get_book_by_id,
    get_mi_by_rndbid,
    get_mi_by_title_sorted,
)
from .parser import (
    _parse_date,
    parse_book_number,
)


class rndblocal(Source):

    name = "RNDB Local"
    description = "Downloading rndb dump for faster search on massive librarys."
    author = "Nyk"
    version = (0, 1, 5)
    minimum_calibre_version = (9, 0, 0)

    #: Set this to True if your plugin returns HTML formatted comments
    has_html_comments = True  # we use <br> instead of \n

    # Plugin capabilities
    capabilities = frozenset({"identify"})

    # Metadata fields this plugin can provide
    touched_fields = frozenset(
        {
            "title",
            "authors",
            "tags",
            "pubdate",
            "comments",
            "publisher",
            "identifiers",
            "series",
            "series_index",
            "languages",
        }
    )

    # Configuration options
    options = (
        Option(
            "language",
            "choices",
            "en",
            "Book language:",
            "Use this option to set the preferences of the language, it might fallback to 'ja' if all english entries are None",
            choices={
                "en": "English",
                "ja": "Japanese",
            },
        ),
        Option(
            "rx",
            "string",
            "vol\\.|volume|book",
            "Santize Vol.|Volume|Book?",
            "THIS MIGHT FUCK UP YOUR TITLE\nUse this in combination with leading zero's function e.g.'Volume [Number]'.",
        ),
        Option(
            "rxr",
            "string",
            "Book",
            "String to sanitize with:",
            "THIS MIGHT FUCK UP YOUR TITLE\nSet this to blank aka '' to use the leading zeros without changing the prefix.",
        ),
        Option(
            "rxn",
            "number",
            2,
            "Leading zero's if number is smaller than?",
            "Leading zero's if len(number) AFTER your searchstring e.g. 'Volume [NUMBER]' is lower than the amount e.g. set to 2 for 1 -> 01",
        ),
        Option(
            "threshold",
            "number",
            60,
            "Threshold in %",
            "Threshold in % 0-100, default 60%",
        ),
        Option(
            "days",
            "number",
            7,
            "Version -x Days:",
            "TBD",
        ),
        Option(
            "force",
            "bool",
            False,
            "Force title search",
            "Ignore any identifier and search by title only. This is usefull if any historic entry might be wrong",
        ),
    )

    def identify(
        self,
        log,
        result_queue,
        abort,
        title=None,
        authors=None,
        identifiers={},
        timeout=30,
    ):
        """
        Identify a book by its title/author/identifiers.

        :param log: Log object for debugging
        :param result_queue: Queue to put Metadata results into
        :param abort: Event to check for abort signal
        :param title: Book title (optional)
        :param authors: List of authors (optional)
        :param identifiers: Dict of identifiers (optional)
        :param timeout: Request timeout in seconds
        :return: None on success, error string on failure
        """
        log.info(
            "RanobeDB: Starting identify for title=%s, authors=%s, identifiers=%s"
            % (title, authors, identifiers)
        )

        log.info("Checking local DB age max=%s" % (self.prefs.get("days", 10)))
        check_local(self.prefs.get("days", 10))
        log.info("Done checking local DB, starting search...")

        rx = re.compile(rf'(?i)((?:{self.prefs.get("rx","")})\s*)(\d+)')

        # Check if we have a RanobeDB ID
        ranobedb_id = identifiers.get("ranobedb")

        if ranobedb_id and not self.prefs.get("force"):
            log.info("RanobeDB: Looking up book by ID: %s" % ranobedb_id)

            if abort.is_set():
                return None

            mi = get_mi_by_rndbid(ranobedb_id, self.prefs.get("language", "en"))

            if mi:
                mi.source_relevance = 1
                mi.title = rx.sub(
                    partial(
                        parse_book_number,
                        prefix=self.prefs.get("rxr", None),
                        width=self.prefs.get("rxn", 2),
                    ),
                    mi.title,
                )
                result_queue.put(mi)
                log.info("RanobeDB: Found book: %s" % mi.title)
            else:
                log.warning("RanobeDB: Book not found with ID: %s" % ranobedb_id)
        else:
            log.info("RanobeDB: Looking up book by title: %s" % title)

            if abort.is_set():
                return None

            book_data = get_mi_by_title_sorted(
                title, self.prefs.get("language", "en"), self.prefs.get("threshold", 60)
            )
            for rank, book in enumerate(book_data):
                log.info("score: %s for book: %s" % (book[0], book[2]))
                mi = get_mi_by_rndbid(int(book[1]), self.prefs.get("language", "en"))
                if mi is None:
                    continue
                mi.source_relevance = rank
                #mi.pubdate = _parse_date(
                #    find_rows("release", "title", book[2])[0].get("release_date"), log
                #)
                mi.title = rx.sub(
                    partial(
                        parse_book_number,
                        prefix=self.prefs.get("rxr", None),
                        width=self.prefs.get("rxn", 2),
                    ),
                    mi.title,
                )
                result_queue.put(mi)

            if result_queue.qsize() == 0:
                log.warning(
                    rf"RanobeDB: Book not found with title: {title}, or below threshold {self.prefs.get("threshold")}%."
                )
        return None

    # has to be reimplemented for the source relevance to work, otherwise it uses the default that ignores the relevance!!
    def identify_results_keygen(self, title=None, authors=None, identifiers={}):
        def keygen(mi):
            return mi.source_relevance

        return keygen
