# Rules comparison: Student A (Colt) vs Student B (Claude as partner)

- **Student A:** Colt Pingilley, [week3-assignment/rules.md](https://github.com/coltping/language-of-computation-week3-assignment/blob/assignment/rules.md)
- **Student B:** Claude, playing partner because no classmate was assigned: `week4-partner/week3/rules.md`

This compares the two rule sets decision by decision. It does **not** judge which is better.

**Agree** = same outcome. **Disagree** = different outcome. **Only A / Only B** = only one set of rules says anything.

## 1. How each kind of ISBN problem is handled

| # | Problem | Student A | Student B | Verdict |
|---|---|---|---|---|
| 1 | Leading zeros dropped from ISBN-10 | Repair + warn | Repair + warn | **Agree** |
| 2 | Lowercase `x` | Repair + warn | Repair + warn | **Agree** |
| 3 | Hyphens / spaces | Repair + warn | Repair + warn | **Agree** |
| 4 | Valid ISBN-13 in the ISBN-10 column | Move it + warn | Move it + warn | **Agree** |
| 5 | Scientific-notation ISBN-13 that matches a valid ISBN-10 | Rebuild from ISBN-10 + warn | Rebuild from ISBN-10 + warn | **Agree** |
| 6 | What "matches" means for a scientific-notation value | Equal after rounding to 12 significant digits (answer 12) | Uses 12 significant digits for candidates; its example 15 treats a shorter value the same way | **Agree** (A states it as a rule; B only through the example) |
| 7 | Scientific notation, no ISBN-10, **one** ISBN-13 fits | Load without ISBN-13 + warn (treated as a guess) | **Repair** to that ISBN-13 + warn | **Disagree** |
| 8 | Scientific notation, no ISBN-10, **two** ISBN-13s fit | Load without ISBN-13 + warn | Load without ISBN + warn | **Agree** |
| 9 | Scientific-notation ISBN-13 that does **not** match the valid ISBN-10 | Load with **neither** ISBN + warn (answer 2) | **Keep the ISBN-10**, calculate the ISBN-13 from it, ignore the rounded value + warn | **Disagree** |
| 10 | ISBN-13 with `978` cut off | Load without ISBN + warn | **Repair** to `978` + value + warn | **Disagree** |
| 11 | Wrong check digit | Load without that ISBN + warn | **Reject** the row | **Disagree** |
| 12 | Letter in the middle | Load without ISBN + warn | **Reject** | **Disagree** |
| 13 | Wrong length after cleaning | Load without ISBN + warn | **Reject** | **Disagree** |
| 14 | Too short and still fails after padding | Load without ISBN + warn | **Reject** | **Disagree** |
| 15 | ISBN-10 and ISBN-13 both valid but different | Load with **neither** + warn | **Reject** | **Disagree** |
| 16 | One column valid, the other broken | Keep the valid one + warn about the broken one (answer 9) | A broken value means **reject** (wrong check digit → reject, whichever column) | **Disagree** |
| 17 | `isbn13` holds a non-ISBN code (UPC, other prefix, decimal, truncated) | Ignore + warn; use a valid ISBN-10 | Ignore + warn; use a valid ISBN-10 | **Agree** |
| 18 | Both ISBN columns empty | Load without ISBN + warn | Load without ISBN + warn | **Agree** |
| 19 | Storing the ISBN-10 | Only if the file gave one; never calculated (answer 5) | **Calculated** from a 978 ISBN-13 when missing | **Disagree** |

## 2. What makes two rows the same book

| # | Decision | Student A | Student B | Verdict |
|---|---|---|---|---|
| 20 | Identity | Same **ISBN-13** after repairs; `book_id` only when there's no usable ISBN | Same **`book_id`** | **Disagree** |
| 21 | ISBN-13 already used by a **different** book_id | Load the new row **without** the ISBN + warn | **Reject** the new row | **Disagree** |
| 22 | Same book_id, **different valid ISBN-13** | **Reject** ("book_id already belongs to a different ISBN") | **Update** to the newer ISBN + warn | **Disagree** |
| 23 | Rounded scientific-notation text is never compared as written | Says so | Says nothing | **Only A** |
| 24 | Exact duplicate row in the same file | Second copy is skipped | Second copy is skipped | **Agree** |

## 3. When a book arrives again

| # | Decision | Student A | Student B | Verdict |
|---|---|---|---|---|
| 25 | Nothing changed | Skip, count as already exists | Skip, count as already exists | **Agree** |
| 26 | Something changed | Update the changed fields | Update the changed fields | **Agree** |
| 27 | Incoming ISBN empty or unusable while the database has one | Keep the old ISBN + warn; counts as skipped if nothing else changed (answer 4) | Keep the old value + warn; counts as skipped if nothing else changed | **Agree** |
| 28 | Empty value arriving for another column | Never overwrites a **required** field (title) | Never overwrites **any** column with an empty value | **Disagree** (in scope) |
| 29 | ISBN warnings on rows skipped on a later run | **Not repeated**; only counted (answer 3) | **Repeated on every run**, so each report is complete on its own | **Disagree** |

## 4. Other columns and rejected rows

| # | Decision | Student A | Student B | Verdict |
|---|---|---|---|---|
| 30 | Which columns the database keeps | All CSV columns (answer 1) | Says nothing | **Only A** |
| 31 | Non-ISBN values (titles, years…) | Stored **exactly as given** (answer 6) | Leading and trailing spaces **trimmed** from every text column | **Disagree** |
| 32 | Reject: book_id missing or not a whole number | Yes | Yes | **Agree** |
| 33 | Reject: empty title | Yes | Yes | **Agree** |
| 34 | Reject: wrong number of columns | Yes | Yes | **Agree** |

## 5. What the report must say

| # | Decision | Student A | Student B | Verdict |
|---|---|---|---|---|
| 35 | When, which file, counts, whether they add up | Yes | Yes | **Agree** |
| 36 | One-line verdict ("All rows accounted for…", "N rejected: action needed", "N with warnings: review") | Yes | Says nothing | **Only A** |
| 37 | Every rejected row with line, book_id, title, value, reason and what to do | Yes | Yes | **Agree** |
| 38 | Every warning with line, book_id, title, value and reason | Yes | Yes | **Agree** |
| 39 | Skipped rows listed one by one | No, only counted (answer 10) | Says nothing | **Only A** |
| 40 | Line numbers, timestamp format, where files are created | File lines with header = 1; local time + offset; next to `ingest.py` (answers 7, 8, 11) | Says nothing | **Only A** |

**Totals:** 40 decisions: 19 agree, 16 disagree, 5 only A, 0 only B. Item 6 counts as agree.

## 6. Examples that end up differently under the other student's rules

### Student A's examples under Student B's rules

| A # | Value | Student A says | Under Student B |
|---|---|---|---|
| 1–6 | `043965548X`, `439023483`, `61120081`, `031200009x`, `0-450-19827-8`, `␣162 001 4750␣` | Valid or repaired | Same |
| 7 | `9781982147600` in isbn | ISBN-13 moved; ISBN-10 empty | Same ISBN-13, **but the ISBN-10 `1982147601` is calculated and stored** |
| 8–10 | `9798351220413`; `9.78043902348e+12` + `439023483`; `9.7804251888e+12` alone | Valid / rebuilt / load without | Same |
| 11 | `1854433017` | Load without ISBN + warn | **Rejected** |
| 12 | `04390A3483` | Load without ISBN + warn | **Rejected** |
| 13 | `15287463097` | Load without ISBN + warn | **Rejected** |
| 14 | `1555550126` + `9781555550134` | Load with neither + warn | **Rejected** |
| 15 | `1416913184` | Load without ISBN + warn | **Repaired** to `9781416913184` (ISBN-10 `1416913181` calculated) |
| 16, 17, 19 | UPC in isbn13 with `553609416`; both empty; `0306406152` | Load as described | Same |
| 18 | `1416524797` on book 10013 | Load without ISBN + warn | **Rejected** |
| 20 | `9780306406158` | Load without ISBN + warn | **Rejected** (wrong check digit) |
| 21, 22 | Book 25 with empty ISBNs; book 106 unchanged | Keep / skip | Same |

**Different: 8 of 22** (A# 7, 11, 12, 13, 14, 15, 18, 20).

### Student B's examples under Student A's rules

| B # | Value | Student B says | Under Student A |
|---|---|---|---|
| 1–4, 6, 7, 9, 17, 18 | Valid, simple repairs, two-candidate rounding, empty, book 25 | As described | Same |
| 5 | `9781982147600` in isbn | Moved; ISBN-10 `1982147601` calculated | ISBN-13 same, **ISBN-10 left empty** |
| 8 | `9.78067172365e+12`, no ISBN-10 | Repaired to `9780671723651` | **Loaded without ISBN-13** + warn |
| 10 | `1416913184` | Repaired to `9781416913184` | **Loaded without ISBN** + warn |
| 11 | `1854433017` | Rejected | **Loaded without ISBN** + warn |
| 12 | `04390A3483` | Rejected | **Loaded without ISBN** + warn |
| 13 | `15287463097` | Rejected | **Loaded without ISBN** + warn |
| 14 | `1555550126` + `9781555550134` | Rejected | **Loaded with neither** + warn |
| 15 | `098870742X` + `9.7809887074e+12` | ISBN-10 kept, ISBN-13 `9780988707429` | **Loaded with neither** + warn |
| 16 | `1416524797` on book 10013 | Rejected | **Loaded without ISBN** + warn |

**Different: 9 of 18** (B# 5, 8, 10, 11, 12, 13, 14, 15, 16).

## 7. What the disagreements would mean for the two real files

These estimates use the counts in Module 3's `data-validation.md`.

| | Student A's rules | Student B's rules |
|---|---|---|
| books.csv rows rejected | 0 | 15 (14 too-short + 1 wrong check digit) |
| books-batch2.csv rows rejected | 0 | 5 (10007, 10008, 10009, 10011, 10013) |
| books.csv rows given an ISBN-13 from a single rounding candidate | 0 | 55 |
| books.csv rows repaired from `978` cut off | 0 | 8 |
| books.csv rows keeping the ISBN-10 when the rounded value doesn't match | 0 (both dropped) | 13 |
| Titles with surrounding spaces trimmed | 0 | Every one that has them |
