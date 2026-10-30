# Reflection — Static Code Analysis

## 1. Which issues were the easiest to fix, and which were the hardest? Why?

The easiest were the Flake8 style issues (two blank lines between functions, wrapping long lines) and the simple Pylint warnings such as unused imports, missing docstrings and `== False`. Each one points to an exact line and has one obvious fix, and none of them change what the program does.

The hardest were the issues that change behaviour. The mutable default argument (`register={}`) looked like a one-line fix, but once the default became `None`, `main()` crashed with a `KeyError` because it had been relying on the shared dictionary to collect every call. I had to change `main()` to create one register and pass it in explicitly. The logic bugs that no tool reported were harder still: finding that 75% was "not eligible", that holidays counted as absences, and that `"2026-9-3"` and a 2030 date were accepted meant reading the output line by line and asking whether it made sense. Replacing the shell `tar` command also needed thought, since the fix had to keep the backup feature working without a shell.

## 2. Did the static analysis tools report any false positives? If so, describe one example.

Mostly the findings were real, but a few were weaker than they looked:

- **Bandit B404** ("consider possible security implications of the subprocess module") is flagged simply because `subprocess` is imported. Importing it is not a vulnerability by itself; the real problem was the `shell=True` call with a wildcard, which B602 and B609 already reported.
- **Bandit B604** flagged `runJob(..., shell=True)`, but `runJob` only returned a dictionary and never executed anything, so in the current code nothing could actually be injected. I still removed it, because a later change could easily make `runJob` run the command.
- Bandit rates B113 (missing timeout) as *Low confidence*, which shows the tool itself is unsure.

There were also **false negatives**: Bandit did not report the hard-coded `ERP_API_KEY` (its hard-coded-password check looks for names such as `password`), and none of the tools caught the CSV formula injection, the off-by-one eligibility rule or the date problems. A clean report does not mean the code is correct.

## 3. How would you integrate static analysis tools into your actual software development workflow?

- **Locally, before every commit:** a `pre-commit` hook that runs Flake8, Pylint and Bandit on the changed files, so problems are fixed before they reach the repository. Editor plugins (e.g. the VS Code Pylint and Flake8 extensions) show warnings while typing.
- **In CI (e.g. GitHub Actions):** run all three tools on every push and pull request, and fail the build if Bandit finds any Medium/High issue, Flake8 reports anything, or the Pylint score drops below an agreed threshold such as 9.5.
- **Shared configuration:** keep the rules in `pyproject.toml` / `.flake8` / `.pylintrc` so everyone uses the same settings, and use `# nosec` or `# pylint: disable=` only with a comment explaining why.
- **Alongside other checks:** static analysis complements, not replaces, unit tests and code review — tests would have caught the 75% and holiday bugs that the tools missed.

## 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Measured:** Pylint went from 4.55/10 to 10.00/10, Bandit from 8 issues (2 High, 3 Medium, 3 Low) to none, and Flake8 from 24 issues to none.
- **Security:** TLS certificates are verified, TLS 1.0 is no longer used, network calls cannot hang forever, there is no shell command to inject into, the API key is no longer in the source code, and exported CSVs cannot run formulas in Excel.
- **Correctness:** the program now gives the right answers — a 75% student is eligible, holidays do not count against students, duplicate and malformed dates do not distort the percentage, and the latest date is actually the latest.
- **Robustness:** bad input is rejected with a clear message instead of corrupting data, files are closed safely with `with`, and a student with no records no longer causes a `ZeroDivisionError`.
- **Readability:** consistent snake_case names, docstrings on every function, simpler boolean expressions and PEP 8 formatting make the file much easier to read and maintain.
