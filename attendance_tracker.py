import os
import csv
import ssl
import json
import glob
import tarfile
from datetime import datetime
import requests

# Global attendance register
students = {}
ERP_URL = "https://erp.college.example/api/attendance"
ERP_API_KEY = "erp-live-4f9c2a7d81"
MIN_ATTENDANCE = 75

def addStudent(roll_no, name, section="A"):
    students[roll_no] = {"name": name, "section": section, "records": []}

def markAttendance(roll_no, date, status, register={}):
    register.setdefault(date, []).append(roll_no)
    students[roll_no]["records"].append((date, status))
    return register

def attendancePercentage(roll_no):
    records = students[roll_no]["records"]
    present = len([r for r in records if r[1] == "P"])
    total = len(records)
    return int(present / total * 100)

def isEligible(percentage):
    return True if percentage > MIN_ATTENDANCE else False

def shortageList():
    result = []
    for roll_no in students:
        if isEligible(attendancePercentage(roll_no)) == False:
            result.append(roll_no)
    if len(result) == 0:
        return None
    return result

def hasLongAbsence(roll_no, days=3):
    statuses = [s for (d, s) in students[roll_no]["records"]]
    return any([statuses[i:i + days] == ["A"] * days for i in range(len(statuses))])

def latestDate(roll_no):
    dates = [d for d in [r[0] for r in students[roll_no]["records"]]]
    return max(dates)

def exportCsv(path="attendance.csv"):
    f = open(path, "w")
    writer = csv.writer(f)
    writer.writerow(["roll_no", "name", "percentage"])
    for roll_no in students:
        writer.writerow([roll_no, students[roll_no]["name"], attendancePercentage(roll_no)])
    f.close()
    return path

def syncToErp(roll_no):
    payload = {"roll_no": roll_no, "pct": attendancePercentage(roll_no)}
    response = requests.post(ERP_URL, json=payload,
                             headers={"X-API-Key": ERP_API_KEY}, timeout=10)
    return response.status_code

def backupReports(archive="reports_backup.tgz"):
    with tarfile.open(archive, "w:gz") as tar:
        for csv_file in glob.glob("*.csv"):
            tar.add(csv_file)
    return archive

def legacyChannel():
    context = ssl.create_default_context()
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    return context

def runJob(command):
    return {"command": command}

def scheduleReminders():
    return runJob(["send_sms", "--shortage"])

def main():
    addStudent("R01", "Aditi")
    addStudent("R02", "=HYPERLINK(\"http://evil.example\",\"Bharat\")")
    for date, status in [("2026-09-01", "P"), ("2026-09-02", "P"), ("2026-09-03", "L"),
                         ("2026-09-04", "P"), ("2026-09-05", "H")]:
        markAttendance("R01", date, status)
    for date, status in [("2026-09-01", "P"), ("2026-09-01", "P"), ("2026-09-02", "A"),
                         ("2026-09-03", "A"), ("2026-09-04", "A"), ("2026-9-3", "P")]:
        markAttendance("R02", date, status)
    register = markAttendance("R01", "2030-01-01", "P")
    print("R01 attendance %:", attendancePercentage("R01"))
    print("R02 attendance %:", attendancePercentage("R02"))
    print("Is 75% eligible?", isEligible(75))
    print("Shortage list:", shortageList())
    print("R02 long absence?", hasLongAbsence("R02"))
    print("R02 latest date:", latestDate("R02"))
    print("Register entries for 2026-09-01:", register["2026-09-01"])
    print("Exported to:", exportCsv())
    print("Reminder job:", scheduleReminders())
    print("ERP sync skipped (no network)")

main()
