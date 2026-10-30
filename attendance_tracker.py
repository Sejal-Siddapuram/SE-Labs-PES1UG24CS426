"""Student attendance tracker.

Marks attendance, applies the 75% rule and exports reports.

Status codes: P = present, A = absent, L = leave (counts as not present),
H = holiday (not a working day, left out of the percentage).
"""
import csv
import os
import ssl
import glob
import tarfile
import datetime
import requests

# Global attendance register
students = {}
ERP_URL = "https://erp.college.example/api/attendance"
MIN_ATTENDANCE = 75
VALID_STATUSES = {"P", "A", "L", "H"}
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def add_student(roll_no, name, section="A"):
    """Register a new student with an empty attendance record."""
    students[roll_no] = {"name": name, "section": section, "records": {}}


def parse_date(text):
    """Return a date from a strict YYYY-MM-DD string that is not in future.

    Raises ValueError for malformed or future dates.
    """
    if len(text) != 10:
        raise ValueError(f"date must be YYYY-MM-DD, got {text!r}")
    day = datetime.datetime.strptime(text, "%Y-%m-%d").date()
    if day > datetime.date.today():
        raise ValueError(f"date {text} is in the future")
    return day


def mark_attendance(roll_no, date, status, register=None):
    """Record a student's status for a date and add them to the register.

    Marking the same date again replaces the earlier status.
    """
    if register is None:
        register = {}
    if roll_no not in students:
        raise ValueError(f"unknown student {roll_no!r}")
    if status not in VALID_STATUSES:
        raise ValueError(f"unknown status {status!r}")
    day = parse_date(date).isoformat()
    students[roll_no]["records"][day] = status
    day_list = register.setdefault(day, [])
    if roll_no not in day_list:
        day_list.append(roll_no)
    return register


def attendance_percentage(roll_no):
    """Return the attendance percentage over working days, to 2 places."""
    statuses = students[roll_no]["records"].values()
    working = [s for s in statuses if s != "H"]
    if not working:
        return 0.0
    present = working.count("P")
    return round(present / len(working) * 100, 2)


def is_eligible(percentage):
    """Return True if the percentage meets the minimum attendance rule."""
    return percentage >= MIN_ATTENDANCE


def shortage_list():
    """Return the roll numbers of students below the attendance minimum."""
    return [roll_no for roll_no in students
            if not is_eligible(attendance_percentage(roll_no))]


def has_long_absence(roll_no, days=3):
    """Return True if the student was absent `days` working days in a row."""
    records = students[roll_no]["records"]
    statuses = [records[day] for day in sorted(records)
                if records[day] != "H"]
    return any(statuses[i:i + days] == ["A"] * days
               for i in range(len(statuses) - days + 1))


def latest_date(roll_no):
    """Return the most recent date recorded for the student, or None."""
    records = students[roll_no]["records"]
    return max(records) if records else None


def safe_cell(value):
    """Stop spreadsheet apps treating a text cell as a formula."""
    text = str(value)
    if text.startswith(FORMULA_PREFIXES):
        return "'" + text
    return text


def export_csv(path="attendance.csv"):
    """Write every student's attendance percentage to a CSV file."""
    with open(path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["roll_no", "name", "percentage"])
        for roll_no, info in students.items():
            writer.writerow([safe_cell(roll_no), safe_cell(info["name"]),
                             attendance_percentage(roll_no)])
    return path


def sync_to_erp(roll_no):
    """Send the student's attendance percentage to the college ERP.

    The API key is read from the ERP_API_KEY environment variable.
    """
    api_key = os.environ.get("ERP_API_KEY")
    if not api_key:
        raise RuntimeError("set the ERP_API_KEY environment variable")
    payload = {"roll_no": roll_no, "pct": attendance_percentage(roll_no)}
    response = requests.post(ERP_URL, json=payload,
                             headers={"X-API-Key": api_key}, timeout=10)
    return response.status_code


def backup_reports(archive="reports_backup.tgz"):
    """Archive all CSV reports in the current folder into a gzip tarball."""
    with tarfile.open(archive, "w:gz") as tar:
        for csv_path in glob.glob("*.csv"):
            tar.add(csv_path)
    return archive


def legacy_channel():
    """Return a TLS context that refuses anything older than TLS 1.2."""
    context = ssl.create_default_context()
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    return context


def run_job(command):
    """Describe a background job; the command is an argument list."""
    return {"command": command}


def schedule_reminders():
    """Schedule SMS reminders for students with an attendance shortage."""
    return run_job(["send_sms", "--shortage"])


def record_day(roll_no, date, status, register):
    """Mark attendance, printing a message instead of crashing on bad input."""
    try:
        mark_attendance(roll_no, date, status, register)
    except ValueError as error:
        print(f"Rejected {roll_no} {date} {status}: {error}")


def main():
    """Run a short demo of the tracker."""
    register = {}
    add_student("R01", "Aditi")
    add_student("R02", "=HYPERLINK(\"http://evil.example\",\"Bharat\")")
    r01_days = [("2026-09-01", "P"), ("2026-09-02", "P"),
                ("2026-09-03", "L"), ("2026-09-04", "P"),
                ("2026-09-05", "H")]
    for date, status in r01_days:
        record_day("R01", date, status, register)
    r02_days = [("2026-09-01", "P"), ("2026-09-01", "P"),
                ("2026-09-02", "A"), ("2026-09-03", "A"),
                ("2026-09-04", "A"), ("2026-9-3", "P")]
    for date, status in r02_days:
        record_day("R02", date, status, register)
    record_day("R01", "2030-01-01", "P", register)
    print("R01 attendance %:", attendance_percentage("R01"))
    print("R02 attendance %:", attendance_percentage("R02"))
    print("Is 75% eligible?", is_eligible(75))
    print("Shortage list:", shortage_list())
    print("R02 long absence?", has_long_absence("R02"))
    print("R02 latest date:", latest_date("R02"))
    print("Register entries for 2026-09-01:", register["2026-09-01"])
    print("Exported to:", export_csv())
    print("Reminder job:", schedule_reminders())
    print("ERP sync skipped (no network)")


if __name__ == "__main__":
    main()
