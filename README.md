# language-of-computation-week4-assignment

This is my Module 4 assignment for MSAI-5523.

**Partner:** Claude (Anthropic's AI assistant). I was not assigned a classmate as a partner, so Claude played the role of my partner. Its partner work, its own Module 3 rules and its separately built database, is kept in a separate, clearly labeled repository: [language-of-computation-week4-partner](https://github.com/coltping/language-of-computation-week4-partner).

All commands below are for **PowerShell on Windows**.

## Open a terminal in this folder

1. Press the **Windows key**, type `PowerShell`, and press **Enter**.
2. Go to the assignment folder:

   ```powershell
   cd $HOME\workspace\language-of-computation\week4-assignment
   ```

## Install what the tests need

The tests use **pytest**. Install it once:

```powershell
python -m pip install pytest
```

## Run the tests

```powershell
python -m pytest -v
```

pytest finds `test_ingest.py`, runs every test, and ends with a summary such as `30 passed in 38s`. It takes about 40 seconds, because several tests load all of books.csv.

The tests use their own temporary `test.db` and log, and delete them afterwards. They never touch `books.db` or `ingestion-log.json` in this folder.

To save what the terminal prints to a file, run the tests like this, then show the file:

```powershell
python -m pytest -v | Out-File -Encoding utf8 test-results-before.txt
```

```powershell
Get-Content test-results-before.txt
```

For the final run, use `test-results.txt` instead of `test-results-before.txt`. `-Encoding utf8` keeps the file readable on GitHub. Without it, Windows PowerShell saves it as UTF-16.

## Run the ingestion

Run these three commands one at a time, in this order:

```powershell
python ingest.py books.csv
```

```powershell
python ingest.py books.csv
```

```powershell
python ingest.py books-batch2.csv
```

Each run prints how many rows were read, loaded, updated, skipped and rejected, and adds an entry to `ingestion-log.json`. `books.db` and `ingestion-log.json` are created in this folder.

To start over, delete them first:

```powershell
Remove-Item books.db, ingestion-log.json
```

## Open the report

```powershell
start report.html
```

Click **Open ingestion-log.json** and choose `ingestion-log.json` from this folder.
