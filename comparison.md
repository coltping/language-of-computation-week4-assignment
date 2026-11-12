# Database comparison: my books.db vs partner/books.db

## Result: the two databases hold the same data

| | Books |
|---|---:|
| My `books.db` | 10,014 |
| My partner's `partner/books.db` | 10,014 |
| Books in both | 10,014 |
| Books only in mine | 0 |
| Books only in my partner's | 0 |
| Books in both with a different value | 0 |

**Partner:** Claude, playing Student B because no classmate was assigned. Its `books.db` was built by its own `ingest.py`, written separately from the agreed `rules.md`. It ran the same three times on byte-identical copies of `books.csv` and `books-batch2.csv`. Source: [language-of-computation-week4-partner](https://github.com/coltping/language-of-computation-week4-partner).

## How the books were compared

- **Same book:** `rules.md` section 3 says two rows are the same book when they have the same ISBN-13. A book with no usable ISBN is matched by `book_id`.
  - 9,272 books were matched by ISBN-13.
  - 742 were matched by `book_id`.
  - No two rows in either database share a key.
- **Columns compared (23):** every column both databases have, matched by name. These are `book_id`, `goodreads_book_id`, `best_book_id`, `work_id`, `books_count`, `isbn10`, `isbn13`, `authors`, `original_publication_year`, `original_title`, `title`, `language_code`, `average_rating`, `ratings_count`, `work_ratings_count`, `work_text_reviews_count`, `ratings_1`, `ratings_2`, `ratings_3`, `ratings_4`, `ratings_5`, `image_url` and `small_image_url`.
- **Left out (2):** `loaded_at` and `updated_at`. Only my partner's database has them, and they only record when a row was written.
- **Values** were compared exactly as stored, including spaces and empty values.
- **Check that the comparison can find differences:** on a temporary copy of my partner's database, I deleted one book (106) and added one space to one title (11). The comparison reported exactly those two differences.

## Books only in mine

None.

## Books only in my partner's

None.

## Books in both with a different value

None.

## Why our data differs

Our data does not differ. Both databases hold the same 10,014 books, with the same value in every one of the 23 columns we both have. Here is why I think that is, and what it does and doesn't prove.

**The rules left nothing to disagree about.** When my partner and I compared our Module 3 rules, we disagreed on 16 decisions: for example, whether a broken ISBN rejects the row, whether to rebuild the 55 rounded ISBN-13s that have only one possible answer, and whether to trim spaces from titles. I settled each one, and in every case I kept my own rule. So the agreed `rules.md` is my Module 3 rules with a few details spelled out. Both programs were built from that one file, and both handle all 24 examples in it the same way.

**The tests and the code had nothing to catch.** My `ingest.py` was already written from those rules, so all 30 tests passed before I changed anything, and I didn't need to change it. My partner's `ingest.py` was written separately, with a different structure, two extra timestamp columns and a different log format. It still follows the same rules, so it produced the same books.

**Where differences would have come from.** If I had picked my partner's side on any of the 16 disagreements, our data would differ, and the difference would trace back to the rule rather than to the tests or the code. Some examples:
- My partner's "reject" rule would have left out 15 books from books.csv and 5 from batch 2.
- Its rebuild rule would have given 55 more books an ISBN-13.
- Its trimming rule would have changed titles like "The Kite Runner ".

The only extra column, `loaded_at`/`updated_at`, was left out on purpose. It records when a row was written, not anything about the book.

**The limits of this result.** I had no classmate partner, so my partner was Claude. Claude also helped write my own `ingest.py`, so the two programs are not as independent as two students' would be. Matching data here shows that two implementations of the same written rules agree on these two files. It is weaker evidence than two classmates arriving at the same answer on their own.
