# Lab 5: Static Code Analysis — Student Attendance Tracker

**Your file:** `attendance_tracker.py`
**Python:** 3.10 or newer

Follow the lab handout for the full instructions.

## About the program

A college attendance tracker. It marks daily attendance per student, works out attendance percentages, applies the 75% exam-eligibility rule, lists students with a shortage, exports a CSV, schedules reminders and can sync to an ERP system and back up reports.

The code works, but only just. It has quality, style and security problems of the kind Pylint, Flake8 and Bandit are built to find.

## What to do

1. **Install the tools:**
   ```bash
   python -m pip install pylint bandit flake8 requests
   ```
   `requests` is installed as well because the program imports it; without it the program stops with `ModuleNotFoundError`.

2. **Run it first** and read the output carefully:
   ```bash
   python attendance_tracker.py
   ```
   It runs a short built-in demo and prints the results; it does not ask for input. Read every line and ask whether a sensible program would print that. Not every problem in this file is something a tool will flag, so pay attention to output that looks wrong.



3. **Run the analysis** and save the reports:
   ```bash
   python -m pylint attendance_tracker.py > pylint_report.txt
   python -m bandit -r attendance_tracker.py > bandit_report.txt
   python -m flake8 attendance_tracker.py > flake8_report.txt
   ```
   Use the `python -m` form: it works everywhere, including Windows where a bare `pylint` is often "not recognized". The tools exit with a non-zero status whenever they find issues; that is expected, not an error. In Windows PowerShell 5.1, `>` saves files as UTF-16; if a report looks garbled, use `python -m pylint attendance_tracker.py | Out-File -Encoding utf8 pylint_report.txt` instead.

4. **Document the issues** in `issues.md` using this table (at least 4 rows, high and medium severity first):

   | Issue | Type | Line(s) | Description | Fix Approach |
   |-------|------|---------|-------------|--------------|
   | ... | ... | ... | ... | ... |

5. **Fix the code.** Fix at least 4 of the issues you documented, then rerun all three tools to confirm they are gone. Repeat until you are satisfied. The program should still do its job when you are done.

6. **Reflect.** Answer the four reflection questions from the handout in `reflection.md`.

## Deliverables

1. `attendance_tracker.py`: your cleaned version, with at least 4 issues fixed.
2. `issues.md`: the completed issue table.
3. `reflection.md`: your answers to the reflection questions.

**Target:** aim for a Pylint score above 9.5 on your final file. A perfect 10.00/10 is very good.

Be ready to explain the bugs you found and how you fixed them. You may be called on to present.
