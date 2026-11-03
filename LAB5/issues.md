# Issues Found and Fixed — `attendance_tracker.py`

Line numbers refer to the **original** file. Severity for Bandit rows is Bandit's own rating.
Tool scores: Pylint **4.55 → 10.00**, Bandit **8 issues → 0**, Flake8 **24 issues → 0**.

## High and medium severity (fixed first)

| # | Issue | Type | Tool / Code | Line(s) | Description | Fix Approach |
|---|-------|------|-------------|---------|-------------|--------------|
| 1 | TLS certificate check disabled | Security (High) | Bandit B501 | 60 | `requests.post(..., verify=False)` accepts any certificate, so the ERP connection can be intercepted (man-in-the-middle). | Removed `verify=False`; requests verifies certificates by default. |
| 2 | Shell command with wildcard | Security (High) | Bandit B609, B602, B607, B404 | 5, 64 | `subprocess.Popen("tar -czf ... *.csv", shell=True)` runs through the shell; a file named like `--checkpoint-action=exec=...` is read by `tar` as an option (wildcard injection). | Replaced with the `tarfile` + `glob` modules, so no shell or external program is used; removed `import subprocess`. |
| 3 | Insecure TLS version | Security (Medium) | Bandit B503 | 66–67 | Default argument `ssl.PROTOCOL_TLSv1` uses TLS 1.0, which is deprecated and broken. | Use `ssl.create_default_context()` with `minimum_version = TLSv1_2`. |
| 4 | Request without timeout | Security / Reliability (Medium) | Bandit B113, Pylint W3101 | 60 | If the ERP server never answers, the program hangs forever. | Added `timeout=10`. |
| 5 | `shell=True` passed to a job | Security (Medium) | Bandit B604 | 73 | `runJob("send_sms --shortage", shell=True)` sets up the reminder to run as a shell string. | Removed the `shell` parameter; the command is passed as a list `["send_sms", "--shortage"]`. |
| 6 | Hard-coded API key | Security (High) | Manual review (no tool flagged it) | 12 | `ERP_API_KEY = "erp-live-..."` is a live secret committed to Git. | Read it from the `ERP_API_KEY` environment variable; raise a clear error if it is missing. The leaked key should also be revoked. |
| 7 | Mutable default argument | Bug | Pylint W0102 | 18 | `register={}` is created once and shared by every call, so registers from different calls mix together (output showed `['R01', 'R02', 'R02']`). | Default to `None`, create a new dict inside, and pass one register explicitly from `main()`. |
| 8 | 75% student marked not eligible | Logic bug | Manual (program output) | 30 | `percentage > MIN_ATTENDANCE` means exactly 75% fails the 75% rule (`Is 75% eligible? False`). | Changed to `>=`. |
| 9 | Malformed and future dates accepted | Logic bug | Manual (program output) | 18–21, 82, 84 | `"2026-9-3"` was stored as a separate day and `"2030-01-01"` (future) was accepted; `latestDate` then returned `2026-9-3` because strings compare character by character. | `parse_date()` accepts only `YYYY-MM-DD` and rejects future dates; dates are stored in one normalised form; `main()` prints a rejection instead of crashing. |
| 10 | Duplicate date counted twice | Logic bug | Manual (program output) | 18–21, 81 | Marking `2026-09-01` twice added two records and two register entries, inflating the total. | Records are a dict keyed by date, so marking a date again replaces it; the register never repeats a roll number. |
| 11 | Holidays counted as absences / divide by zero | Logic bug | Manual review | 23–27 | `H` (holiday) counted as a missed working day; `int()` truncated 66.67 to 66; a student with no records crashed with `ZeroDivisionError`. | Exclude `H` from working days, round to 2 decimals, return `0.0` when there are no working days. |
| 12 | CSV formula injection | Security (Medium) | Manual review | 54, 77 | A name like `=HYPERLINK("http://evil.example",...)` is written raw to the CSV and runs as a formula when opened in Excel. | `safe_cell()` prefixes `'` to any cell starting with `= + - @`, tab or carriage return. |

## Lower severity (style / quality)

| # | Issue | Type | Tool / Code | Line(s) | Description | Fix Approach |
|---|-------|------|-------------|---------|-------------|--------------|
| 13 | File opened without `with` / encoding | Quality | Pylint R1732, W1514 | 50–55 | File may stay open if an error occurs; encoding depends on the OS. | `with open(path, "w", encoding="utf-8", newline="")`. |
| 14 | Unused imports | Quality | Pylint W0611, Flake8 F401 | 1, 4, 6 | `os`, `json`, `datetime` imported but not used. | Removed (`os` and `datetime` were later used properly by fixes 6 and 9). |
| 15 | camelCase function names | Style | Pylint C0103 | 15–75 | Names like `addStudent` break PEP 8 snake_case. | Renamed to `add_student`, `mark_attendance`, etc. |
| 16 | Missing docstrings | Style | Pylint C0114, C0116 | 1, all functions | No module or function documentation. | Added a module docstring and one per function. |
| 17 | Redundant boolean code | Quality | Pylint R1719, C0121, Flake8 E712 | 30, 35 | `True if x else False` and `== False`. | `return percentage >= ...` and `if not is_eligible(...)`. |
| 18 | `shortageList` returned `None` | Quality | Manual review | 37–38 | Callers had to handle two return types. | Always returns a list (possibly empty). |
| 19 | List inside `any()`, needless comprehension, dict iteration | Quality | Pylint R1729, R1721, C0206 | 43, 46, 53 | Builds unnecessary lists. | Generator in `any()`, simplified comprehension, `students.items()`. |
| 20 | Blank lines | Style | Flake8 E302, E305 | 15–96 | One blank line between top-level functions instead of two. | Two blank lines around every function. |
| 21 | Long lines | Style | Flake8 E501, Pylint C0301 | 43, 54, 60, 78, 81, 82 | Lines over 79 characters. | Wrapped the lines; split the demo data into named lists. |
| 22 | No `__main__` guard | Quality | Manual review | 96 | Importing the module ran the demo. | `if __name__ == "__main__": main()`. |

## Program output before and after

| Line printed | Before | After |
|--------------|--------|-------|
| R01 attendance % | 66 | 75.0 |
| R02 attendance % | 50 | 25.0 |
| Is 75% eligible? | False | True |
| Shortage list | ['R01', 'R02'] | ['R02'] |
| R02 latest date | 2026-9-3 | 2026-09-04 |
| Register for 2026-09-01 | ['R01', 'R02', 'R02'] | ['R01', 'R02'] |
| Bad input | silently accepted | `Rejected R02 2026-9-3 P: ...` and `Rejected R01 2030-01-01 P: ...` |
