from calibre.ebooks.metadata.sources.base import Option, Source

import re
import difflib
import json

from .localdb import check_local, find_rows, find_rows_fuzzy, get_book_by_id, get_mi_by_rndbid, get_mi_by_title_sorted
from .parser import _parse_date

san_pattern = re.compile(r'(?i)(?:vol\.|volume|book)')

class rndblocal(Source):

    name = "RNDB Local"
    description = "Downloading rndb dump for faster search on massive librarys."
    author = "Nyk"
    version = (0, 1, 2)
    minimum_calibre_version = (9, 0, 0)

    #: Set this to True if your plugin returns HTML formatted comments
    has_html_comments = True #we use <br> instead of \n

    # Plugin capabilities
    capabilities = frozenset({"identify"})

    # Metadata fields this plugin can provide
    touched_fields = frozenset(
        {
            'title',
            'authors',
            'tags',
            'pubdate',
            'comments',
            'publisher',
            'identifiers',
            'series',
            'series_index',
            'languages',
        }
    )

    # Configuration options
    options = (
        Option(
            "language",
            "choices",
            "en",
            _("Description language:"),
            _("Preferred language for book descriptions"),
            choices={
                "en": _("English"),
                "ja": _("Japanese"),
            },
        ),
        Option(
            "Sanitize",
            "bool",
            True,
            _("Santize Vol.|Volume|Book?"),
            _("THIS MIGHT FUCK UP YOUR TITLE"),            
        ),
        Option(
            "san_string",
            "string",
            "Book",
            _("String to sanitize with:"),
            _("THIS MIGHT FUCK UP YOUR TITLE"),
        ),
        Option(
            "threshold",
            "number",
            60,
            _("Threshold in %"),
            _("Threshold in % 0-100, default 60%"),
        ),
        
        Option(
            "days",
            "number",
            7,
            _("Version -x Days:"),
            _("TBD"),
        ),
        Option(
            "force",
            "bool",
            False,
            _("Force title search"),
            _(
                "Ignore any identifier and search by title only. This is usefull if any historic entry might be wrong"
            ),
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

        # Check if we have a RanobeDB ID
        ranobedb_id = identifiers.get("ranobedb")

        if ranobedb_id and not self.prefs.get("force"):
            log.info("RanobeDB: Looking up book by ID: %s" % ranobedb_id)

            if abort.is_set():
                return None

            mi = get_mi_by_rndbid(ranobedb_id,self.prefs.get("language", "en"))

            if mi:
                mi.source_relevance = 1
                if self.prefs.get("Sanitize", True):
                    mi.title = san_pattern.sub(self.prefs.get('san_string','Book'), mi.title)
                result_queue.put(mi)
                log.info("RanobeDB: Found book: %s" % mi.title)
            else:
                log.warning("RanobeDB: Book not found with ID: %s" % ranobedb_id)
        else:
            log.info("RanobeDB: Looking up book by title: %s" % title)

            if abort.is_set():
                return None

            book_data = get_mi_by_title_sorted(title,self.prefs.get("language", "en"),self.prefs.get("threshold", 60))
            for rank, book in enumerate(book_data):
                log.info("score: %s for book: %s" % (book[0],book[2]))
                mi = get_mi_by_rndbid(int(book[1]),self.prefs.get("language", "en"))
                if mi is None:
                    continue
                mi.source_relevance = rank
                mi.pubdate = _parse_date(find_rows("release","title",book[2])[0].get('release_date'), log)
                if self.prefs.get("Sanitize", True):
                    mi.title = san_pattern.sub(self.prefs.get('san_string','Book'), mi.title)
                result_queue.put(mi)

            if result_queue.qsize() == 0:
                log.warning(
                    "RanobeDB: Book not found with title: %s, or below threshold %s."
                    % (title, self.prefs.get("threshold"))
                )
        return None

    # has to be reimplemented for the source relevance to work, otherwise it uses the default that ignores the relevance!!
    def identify_results_keygen(self, title=None, authors=None, identifiers={}):
        def keygen(mi):
            return mi.source_relevance

        return keygen
