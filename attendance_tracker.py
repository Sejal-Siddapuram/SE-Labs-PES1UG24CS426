"""Student attendance tracker: marks attendance, applies the 75% rule and exports reports."""
import csv
import ssl
import glob
import tarfile
import requests

# Global attendance register
students = {}
ERP_URL = "https://erp.college.example/api/attendance"
ERP_API_KEY = "erp-live-4f9c2a7d81"
MIN_ATTENDANCE = 75

def add_student(roll_no, name, section="A"):
    """Register a new student with an empty attendance record."""
    students[roll_no] = {"name": name, "section": section, "records": []}

def mark_attendance(roll_no, date, status, register=None):
    """Record a student's status for a date and add them to the day register."""
    if register is None:
        register = {}
    register.setdefault(date, []).append(roll_no)
    students[roll_no]["records"].append((date, status))
    return register

def attendance_percentage(roll_no):
    """Return the student's attendance percentage."""
    records = students[roll_no]["records"]
    present = len([r for r in records if r[1] == "P"])
    total = len(records)
    return int(present / total * 100)

def is_eligible(percentage):
    """Return True if the percentage meets the minimum attendance rule."""
    return percentage > MIN_ATTENDANCE

def shortage_list():
    """Return the roll numbers of students below the attendance minimum."""
    result = []
    for roll_no in students:
        if not is_eligible(attendance_percentage(roll_no)):
            result.append(roll_no)
    if len(result) == 0:
        return None
    return result

def has_long_absence(roll_no, days=3):
    """Return True if the student was absent for `days` consecutive records."""
    statuses = [status for (_, status) in students[roll_no]["records"]]
    return any(statuses[i:i + days] == ["A"] * days for i in range(len(statuses)))

def latest_date(roll_no):
    """Return the most recent date recorded for the student."""
    dates = [record[0] for record in students[roll_no]["records"]]
    return max(dates)

def export_csv(path="attendance.csv"):
    """Write every student's attendance percentage to a CSV file."""
    with open(path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["roll_no", "name", "percentage"])
        for roll_no, info in students.items():
            writer.writerow([roll_no, info["name"], attendance_percentage(roll_no)])
    return path

def sync_to_erp(roll_no):
    """Send the student's attendance percentage to the college ERP."""
    payload = {"roll_no": roll_no, "pct": attendance_percentage(roll_no)}
    response = requests.post(ERP_URL, json=payload,
                             headers={"X-API-Key": ERP_API_KEY}, timeout=10)
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
    """Describe a background job; the command is an argument list, never a shell string."""
    return {"command": command}

def schedule_reminders():
    """Schedule SMS reminders for students with an attendance shortage."""
    return run_job(["send_sms", "--shortage"])

def main():
    """Run a short demo of the tracker."""
    register = {}
    add_student("R01", "Aditi")
    add_student("R02", "=HYPERLINK(\"http://evil.example\",\"Bharat\")")
    for date, status in [("2026-09-01", "P"), ("2026-09-02", "P"), ("2026-09-03", "L"),
                         ("2026-09-04", "P"), ("2026-09-05", "H")]:
        mark_attendance("R01", date, status, register)
    for date, status in [("2026-09-01", "P"), ("2026-09-01", "P"), ("2026-09-02", "A"),
                         ("2026-09-03", "A"), ("2026-09-04", "A"), ("2026-9-3", "P")]:
        mark_attendance("R02", date, status, register)
    mark_attendance("R01", "2030-01-01", "P", register)
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
