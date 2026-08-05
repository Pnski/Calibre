from calibre.ebooks.metadata.sources.base import Option, Source

import re

class rndblocal(Source):

    name = "RNDB Local"
    description = "Downloading rndb dump for faster search on massive librarys."
    author = "Nyk"
    version = (0, 0, 1)
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

        rx = re.compile(rf'(?i)((?:{self.prefs.get("rx","")})\s*)(\d+)')

        return None

    # has to be reimplemented for the source relevance to work, otherwise it uses the default that ignores the relevance!!
    def identify_results_keygen(self, title=None, authors=None, identifiers={}):
        def keygen(mi):
            return mi.source_relevance

        return keygen