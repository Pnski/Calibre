from calibre.constants import cache_dir

from calibre.ebooks.metadata.book.base import Metadata

import os, time, shutil, gzip, re, sqlite3, difflib

from .remotedb import download_db
from .parser import _parse_date

# Local file path
cache = os.path.join(cache_dir(), "rndb-db-dump")
os.makedirs(cache, exist_ok=True)

local_file = os.path.join(cache, "rndb-db-public-latest.dump.gz")
db_file = os.path.join(cache, "rndb-db-public-latest.db")


def check_local(days):
    if not os.path.exists(db_file) or check_local_date(days):
        download_db(local_file)
        try:
            os.remove(db_file)
        except FileNotFoundError:
            pass
        create_db()
    return check_local_date(days)


def check_local_date(days=0):
    try:
        mtime = os.path.getmtime(db_file)
        cutoff = time.time() - (days * 24 * 60 * 60)
        return mtime < cutoff  # True => older than 7 days
    except OSError:
        return False

def create_db():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("PRAGMA journal_mode=OFF")
    cursor.execute("PRAGMA synchronous=OFF")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA cache_size=-100000")   # ~100 MB cache
    cursor.execute("PRAGMA locking_mode=EXCLUSIVE")
    BATCH_SIZE = 20000

    with gzip.open(local_file, "rt", encoding="utf-8") as f:

        inside_copy = False
        table = None
        placeholders = None
        batch = []

        for line in f:

            if line.startswith("COPY "):
                match = re.match(
                    r'COPY public\.(?:"([^"]+)"|(\w+)) \((.*?)\) FROM stdin;',
                    line
                )

                if match:
                    table = match.group(1) or match.group(2)
                    columns = [c.strip().strip('"') for c in match.group(3).split(",")]

                    cursor.execute(f'''
                        CREATE TABLE IF NOT EXISTS "{table}" (
                            {",".join(f'"{c}" TEXT' for c in columns)}
                        )
                    ''')

                    placeholders = ",".join("?" for _ in columns)
                    batch.clear()
                    inside_copy = True
                    continue

            if not inside_copy:
                continue

            if line.strip() == r"\.":

                if batch:
                    cursor.executemany(
                        f'INSERT INTO "{table}" VALUES ({placeholders})',
                        batch
                    )
                    batch.clear()

                conn.commit()

                inside_copy = False
                table = None
                placeholders = None
                continue

            batch.append([
                None if x == r"\N" else x
                for x in line.rstrip("\n").split("\t")
            ])

            if len(batch) >= BATCH_SIZE:
                cursor.executemany(
                    f'INSERT INTO "{table}" VALUES ({placeholders})',
                    batch
                )
                batch.clear()

    conn.commit()
    conn.close()

def create_db_old():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    columns = None

    with gzip.open(local_file, "rt", encoding="utf-8") as f:

        inside_copy = False
        table = None
        columns = None
        placeholders = None

        for line in f:

            # Detect COPY table blocks
            if line.startswith("COPY "):

                match = re.match(
                    r'COPY public\.(?:"([^"]+)"|(\w+)) \((.*?)\) FROM stdin;', line
                )

                if match:
                    table = match.group(1) or match.group(2)

                    columns = [c.strip().strip('"') for c in match.group(3).split(",")]

                    # Create SQLite table automatically
                    cursor.execute(
                        f"""
                        CREATE TABLE IF NOT EXISTS "{table}" (
                            {",".join(
                                f'"{c}" TEXT'
                                for c in columns
                            )}
                        )
                        """
                    )

                    placeholders = ",".join("?" for _ in columns)

                    inside_copy = True
                    continue

            if inside_copy:

                # End of COPY section
                if line.strip() == r"\.":
                    conn.commit()

                    inside_copy = False
                    table = None
                    columns = None
                    continue

                values = [
                    None if x == r"\N" else x for x in line.rstrip("\n").split("\t")
                ]

                cursor.execute(
                    f"""
                    INSERT INTO "{table}"
                    VALUES ({placeholders})
                    """,
                    values,
                )
    conn.commit()
    conn.close()


def find_rows(table, column, value, limit=20):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row  # enables dict-like row access
    cur = conn.cursor()

    cur.execute(
        f'SELECT * FROM "{table}" WHERE "{column}" = ? LIMIT ?',
        (value, limit),
    )
    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def find_rows_fuzzy(table, column, value, limit=20):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        f'SELECT * FROM "{table}" WHERE "{column}" LIKE ? LIMIT ?',
        (f"%{value}%", limit),
    )
    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_book_by_id(book_id, limit=5):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            *
        FROM "book" b
        LEFT JOIN "book_edition" be
            ON be.book_id = b.id
        LEFT JOIN "series_book" sb
            ON sb.book_id = b.id
        LEFT JOIN "book_title" bt
            ON bt.book_id = b.id
        LEFT JOIN "series_title" st
            ON st.series_id = sb.series_id
        WHERE b.id = ?
        LIMIT ?
    """,
        (book_id, limit),
    )

    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_mi_by_rndbid(book_id: int, language: str):

    with sqlite3.connect(db_file) as sql:
        title = sql.execute(
            """
            SELECT
                COALESCE(romaji, title)
            FROM book_title
            WHERE 
                book_id = ?
                AND lang IN (?, 'ja')
            ORDER BY
                CASE lang WHEN ? THEN 0 ELSE 1 END
            LIMIT 1
            """,
            (str(book_id), language, language),
        ).fetchone()[0]
        authors = [
            f"{n.split(' ', 1)[1]} {n.split(' ', 1)[0]}" if " " in n else n
            for n, in sql.execute(
                """
                SELECT
                    CASE
                        WHEN ? = 'en' THEN COALESCE(romaji, name)
                        ELSE name
                    END
                FROM "staff_alias" sa
                JOIN "book_staff_alias" bsa
                    ON sa.staff_id = bsa.staff_alias_id
                WHERE
                    bsa.book_id = ?
                    AND bsa.role_type IN ('author', 'artist')
                    and sa.main_alias = 't'
                ORDER BY CASE bsa.role_type
                    WHEN 'author' THEN 0
                    WHEN 'artist' THEN 1
                END
                """,
                (
                    language,
                    str(book_id),
                ),
            ).fetchall()
        ]
        mi = Metadata(title, authors)
        mi.language = language
        mi.comments = (
            sql.execute(
                """
            SELECT
                CASE
                    WHEN ? = 'en' THEN description
                    ELSE description_ja
                END
            FROM book
            WHERE 
                id = ?
            """,
                (
                    language,
                    str(book_id),
                ),
            )
            .fetchone()[0]
            .replace("\\n", "<br>")
        )
        #SUBSTR(rl.amazon, INSTR(rl.amazon, '/dp/') + 4),
        identifiers = sql.execute(
            """
            SELECT
                isbn13,
                rl.website,
                replace(rl.amazon, rtrim(rl.amazon, replace(rl.amazon, '/', '')), ''),
                rl.bookwalker,
                rl.rakuten,
                rl.release_date,
                pub.name
            FROM "release" rl
            JOIN "release_book" rb
                ON rb.release_id = rl.id
            JOIN "release_publisher" rp
                ON rb.release_id = rp.release_id
            JOIN "publisher" pub
                ON rp.publisher_id = pub.id
            WHERE
                rb.book_id = ?
                AND rl.format = 'digital'
                AND lang IN (?, 'ja')
                AND rp.publisher_type = 'publisher'
            ORDER BY
                CASE lang WHEN ? THEN 0 ELSE 1 END
            LIMIT 1
            """,
            (
                str(book_id),
                language,
                language,
            ),
        ).fetchone()
        mi.series, mi.series_index = sql.execute(
            """
            SELECT
                st.title,
                sb.sort_order
            FROM "series_title" st
            JOIN "series_book" sb
                ON sb.series_id = st.series_id
            WHERE
                sb.book_id = ?
                AND st.lang = ?
            """,
            (
                str(book_id),
                language,
            ),
        ).fetchone()
        mi.tags = [
            t[0].title()
            for t in sql.execute(
                """
            SELECT
                tag.name
            FROM "tag" tag
            JOIN "series_tag" st
                ON tag.id = st.tag_id
            JOIN "series_book" sb
                ON st.series_id = sb.series_id
            WHERE
                sb.book_id = ?
            """,
                (str(book_id),),
            ).fetchall()
        ]

    mi.identifiers["ranobedb"] = str(book_id)
    try:
        for key, value in zip(
            ("isbn13", "website", "amazon", "bookwalker", "rakuten"),
            identifiers,
        ):
            if value is not None:
                mi.identifiers[key] = value
        mi.pubdate = _parse_date(identifiers[5])
        mi.publisher = identifiers[6]
    except Exception as e:
        print("Error", e)
    return mi


def get_mi_by_title_sorted(book_title: str, language: str, threshold: int):
    # split into parts for multi search
    parts = re.findall(r"[A-Za-z]+", book_title)
    if not parts:
        return None  # Error in title?

    with sqlite3.connect(db_file) as sql:
        rows = set()

        for part in parts:
            #skipping rly small parts
            if len(part) <= 3 or part in ['Volume', 'Vol.', 'Book']:
                continue
            rows.update(
                sql.execute(
                    """
                SELECT DISTINCT
                    r.title,
                    rb.book_id
                FROM release r
                JOIN release_book rb
                    ON rb.release_id = r.id
                WHERE 
                    r.title LIKE ?
                    AND r.lang = ?
            """,
                    (
                        f"%{part}%",
                        language,
                    ),
                ).fetchall()
            )
            rows.update(
                sql.execute(
                    """
                SELECT DISTINCT
                    title,
                    book_id
                FROM book_title
                WHERE 
                    title LIKE ?
                    AND lang = ?
            """,
                    (
                        f"%{part}%",
                        language,
                    ),
                ).fetchall()
            )
    score_result = sorted(
        {
            (
                difflib.SequenceMatcher(
                    None, book_title.lower(), title.lower()
                ).ratio(),
                book_id,
                title,
            )
            for title, book_id in rows
            if [int(x) for x in re.findall(r"\d+", book_title)]
            == [int(x) for x in re.findall(r"\d+", title)]
        },
        reverse=True,
    )

    if score_result:
        print("best result", score_result[0])

    return [r for r in score_result if r[0] >= (threshold / 100)][:10]
