"""Tests that ingest.py does what rules.md says.

rules.md is the only source of truth: each test names the rule it comes from.

Every test works in its own temporary folder, with a database named test.db and its own
log file. Both are deleted when the test ends, whether it passed or failed. The books.db
and ingestion-log.json in this folder are never touched; a check at the end of every
test proves it.
"""
import csv
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from contextlib import closing

import pytest

import ingest

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS = os.path.join(HERE, "books.csv")
BATCH2 = os.path.join(HERE, "books-batch2.csv")
REAL_FILES = [os.path.join(HERE, "books.db"), os.path.join(HERE, "ingestion-log.json")]


# ---------------------------------------------------------------------------
# Setup and teardown
# ---------------------------------------------------------------------------

def _state(path):
    """Enough to tell whether a file was created, changed or deleted."""
    if not os.path.exists(path):
        return None
    st = os.stat(path)
    return (st.st_size, st.st_mtime_ns)


class Workspace:
    """A temporary folder with test.db and a test log, and a way to run ingest.py on it."""

    def __init__(self, folder, monkeypatch, capsys):
        self.folder = folder
        self.db_path = os.path.join(folder, "test.db")
        self.log_path = os.path.join(folder, "test-ingestion-log.json")
        self._monkeypatch = monkeypatch
        self._capsys = capsys
        # Point ingest.py at test.db and the test log instead of books.db / ingestion-log.json.
        monkeypatch.setattr(ingest, "DB_PATH", self.db_path)
        monkeypatch.setattr(ingest, "LOG_PATH", self.log_path)

    def run(self, csv_path):
        """Run ingest.py on a file, exactly as from the terminal, and return this run's log entry."""
        self._monkeypatch.setattr(sys, "argv", ["ingest.py", csv_path])
        exit_code = ingest.main()
        self._capsys.readouterr()  # keep ingest.py's printout out of the test report
        assert exit_code == 0, f"ingest.py failed on {csv_path}"
        return self.log()[-1]

    def log(self):
        with open(self.log_path, encoding="utf-8") as f:
            return json.load(f)

    def connect(self):
        """A connection to test.db that is closed when the `with` block ends.
        (sqlite3's own `with` only commits; an open connection would lock test.db on Windows.)"""
        return closing(sqlite3.connect(self.db_path))

    def book(self, book_id):
        with self.connect() as conn:
            conn.row_factory = sqlite3.Row
            return conn.execute("SELECT * FROM books WHERE book_id = ?", (book_id,)).fetchone()

    def dump(self):
        """Every table, its structure and every row, in a fixed order."""
        with self.connect() as conn:
            tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
            out = {}
            for t in tables:
                schema = conn.execute("SELECT sql FROM sqlite_master WHERE name = ?", (t,)).fetchone()[0]
                rows = conn.execute(f'SELECT * FROM "{t}" ORDER BY 1').fetchall()
                out[t] = (schema, rows)
            return out

    def write_csv(self, name, rows):
        path = os.path.join(self.folder, name)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=HEADER)
            writer.writeheader()
            writer.writerows(rows)
        return path


@pytest.fixture
def ws(monkeypatch, capsys):
    before = {p: _state(p) for p in REAL_FILES}
    folder = tempfile.mkdtemp(prefix="ingest-test-")
    try:
        yield Workspace(folder, monkeypatch, capsys)
    finally:
        shutil.rmtree(folder, ignore_errors=True)  # removes test.db, the test log and test CSVs
        assert not os.path.exists(folder), "teardown did not remove the test folder"
        after = {p: _state(p) for p in REAL_FILES}
        assert after == before, "a test touched books.db or ingestion-log.json in the assignment folder"


# ---------------------------------------------------------------------------
# Rows for the examples
# ---------------------------------------------------------------------------

def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, {r["book_id"]: r for r in reader}


HEADER, BOOKS_ROWS = _read(BOOKS)
_, BATCH2_ROWS = _read(BATCH2)


def example_row(n, isbn, isbn13):
    """A book row for example n. Only the ISBN columns matter; the rest is copied from book 1."""
    row = dict(BOOKS_ROWS["1"])
    row.update(book_id=str(900000 + n), title=f"Example {n}", original_title=f"Example {n}",
               isbn=isbn, isbn13=isbn13)
    return row


def warnings_for(entry, book_id):
    return [w for w in entry["warnings"] if w["book_id"] == book_id]


# ---------------------------------------------------------------------------
# rules.md section 7: one test per example
#
# Each case: (example #, isbn column, isbn13 column, stored ISBN-10, stored ISBN-13, warned?)
#   - "Load."                         -> no warning                    (section 2)
#   - "Repair ... + warn"             -> repaired value stored, warning (section 2)
#   - "Load without ISBN + warn"      -> loaded, ISBN empty, warning    (section 2)
#   - stored ISBN-10 = cleaned value from the isbn column only           (section 6, item 5)
#   - every warning shows the original value                             (section 2)
# ---------------------------------------------------------------------------

SINGLE_ROW_EXAMPLES = [
    (1, "043965548X", "", "043965548X", "9780439655484", False),
    (2, "439023483", "", "0439023483", "9780439023481", True),
    (3, "61120081", "", "0061120081", "9780061120084", True),
    (4, "031200009x", "", "031200009X", "9780312000097", True),
    (5, "0-450-19827-8", "", "0450198278", "9780450198274", True),
    (6, " 162 001 4750 ", "", "1620014750", "9781620014752", True),
    (7, "9781982147600", "", None, "9781982147600", True),
    (8, "", "9798351220413", None, "9798351220413", False),
    (9, "439023483", "9.78043902348e+12", "0439023483", "9780439023481", True),
    (10, "", "9.7804251888e+12", None, None, True),
    (11, "1854433017", "", None, None, True),
    (12, "04390A3483", "", None, None, True),
    (13, "15287463097", "", None, None, True),
    (14, "1555550126", "9781555550134", None, None, True),
    (15, "1416913184", "", None, None, True),
    (16, "553609416", "76783609419.0", "0553609416", "9780553609417", True),
    (17, "", "", None, None, True),
    (19, "0306406152", "", "0306406152", "9780306406157", False),
    (20, "", "9780306406158", None, None, True),
    (23, "", "9.78067172365e+12", None, None, True),
    (24, "098870742X", "9.7809887074e+12", None, None, True),
]


@pytest.mark.parametrize("n, isbn, isbn13, want10, want13, warned", SINGLE_ROW_EXAMPLES,
                         ids=[f"example-{c[0]}" for c in SINGLE_ROW_EXAMPLES])
def test_example(ws, n, isbn, isbn13, want10, want13, warned):
    path = ws.write_csv(f"example{n}.csv", [example_row(n, isbn, isbn13)])
    entry = ws.run(path)
    book_id = 900000 + n

    # Every example is loaded; none is rejected (section 2: only section 4's cases are rejected).
    assert entry["counts"]["loaded"] == 1
    assert entry["counts"]["rejected"] == 0
    book = ws.book(book_id)
    assert book is not None, f"example {n} was not loaded"

    assert book["isbn10"] == want10
    assert book["isbn13"] == want13

    ws_ = warnings_for(entry, book_id)
    if warned:
        assert ws_, f"example {n} should have a warning"
        originals = " ".join(str(w["original"]) for w in ws_)
        for raw in (isbn, isbn13):
            if raw.strip():
                assert raw.strip() in originals, f"the warning must show the original value {raw!r}"
    else:
        assert ws_ == [], f"example {n} should load with no warning"


def test_example_18_isbn_already_belongs_to_another_book(ws):
    """Example 18 / section 3: an ISBN-13 that belongs to another book_id is loaded without the ISBN, with a warning."""
    path = ws.write_csv("example18.csv", [BOOKS_ROWS["9"], BATCH2_ROWS["10013"]])
    entry = ws.run(path)

    assert entry["counts"]["loaded"] == 2
    assert entry["counts"]["rejected"] == 0
    assert ws.book(9)["isbn13"] == "9781416524793"
    paper_moons = ws.book(10013)
    assert paper_moons is not None
    assert paper_moons["isbn10"] is None and paper_moons["isbn13"] is None
    warnings = warnings_for(entry, 10013)
    assert warnings and "1416524797" in " ".join(w["original"] for w in warnings)


def test_example_21_existing_isbn_is_not_downgraded(ws):
    """Example 21 / section 4 / section 6 item 4: book 25 arrives with empty ISBNs; keep the old ones, skip + warn."""
    ws.run(ws.write_csv("first.csv", [BOOKS_ROWS["25"]]))
    assert ws.book(25)["isbn13"] == "9780545010221"

    entry = ws.run(ws.write_csv("second.csv", [BATCH2_ROWS["25"]]))
    assert entry["counts"]["skipped_already_exist"] == 1
    assert entry["counts"]["updated"] == 0
    assert ws.book(25)["isbn10"] == "0545010225"
    assert ws.book(25)["isbn13"] == "9780545010221"
    assert warnings_for(entry, 25), "keeping the old ISBN must be warned about"


def test_example_22_unchanged_book_is_skipped(ws):
    """Example 22 / section 4: book 106 arrives again unchanged; skip, no warning."""
    ws.run(ws.write_csv("first.csv", [BOOKS_ROWS["106"]]))
    before = tuple(ws.book(106))

    entry = ws.run(ws.write_csv("second.csv", [BATCH2_ROWS["106"]]))
    assert entry["counts"]["skipped_already_exist"] == 1
    assert entry["counts"]["loaded"] == 0 and entry["counts"]["updated"] == 0
    assert tuple(ws.book(106)) == before
    assert warnings_for(entry, 106) == []  # section 6 item 3: skipped rows don't repeat warnings


def test_examples_table_is_fully_covered():
    """Every example in rules.md section 7 has a test above."""
    covered = {c[0] for c in SINGLE_ROW_EXAMPLES} | {18, 21, 22}
    assert covered == set(range(1, 25))


# ---------------------------------------------------------------------------
# Required tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("csv_path", [BOOKS, BATCH2], ids=["books.csv", "books-batch2.csv"])
def test_running_same_file_twice_creates_no_duplicates(ws, csv_path):
    """Section 4: running the same file twice loads nothing new the second time."""
    ws.run(csv_path)
    first = ws.dump()

    second_run = ws.run(csv_path)
    assert second_run["counts"]["loaded"] == 0
    assert second_run["counts"]["updated"] == 0
    assert ws.dump() == first

    with ws.connect() as conn:
        total, ids = conn.execute("SELECT COUNT(*), COUNT(DISTINCT book_id) FROM books").fetchone()
        with_isbn, distinct_isbn = conn.execute(
            "SELECT COUNT(isbn13), COUNT(DISTINCT isbn13) FROM books").fetchone()
    assert total == ids, "the same book_id is in the database more than once"
    assert with_isbn == distinct_isbn, "the same ISBN-13 is in the database more than once"


def test_every_run_adds_a_log_entry_without_overwriting(ws):
    """Every run adds an entry to the log; earlier entries are never changed or removed."""
    files = [BATCH2, BATCH2, BATCH2]
    history = []
    for i, f in enumerate(files, start=1):
        ws.run(f)
        log = ws.log()
        assert len(log) == i, f"after {i} runs the log should have {i} entries"
        assert log[:-1] == history, "an earlier log entry was changed or removed"
        assert log[-1]["file"] == os.path.basename(f)
        history = log


def test_counts_add_up(ws):
    """Section 5: rows read = loaded + updated + skipped + rejected, for every run."""
    for f in (BOOKS, BOOKS, BATCH2):
        c = ws.run(f)["counts"]
        assert c["read"] == c["loaded"] + c["updated"] + c["skipped_already_exist"] + c["rejected"], \
            f"counts don't add up for {os.path.basename(f)}: {c}"


def test_same_file_on_empty_database_gives_same_database(ws):
    """The same file always gives the same result: two runs on an empty database produce identical databases."""
    ws.run(BOOKS)
    first = ws.dump()

    os.remove(ws.db_path)
    os.remove(ws.log_path)
    ws.run(BOOKS)
    assert ws.dump() == first
