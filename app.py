import streamlit as st
import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from dotenv import load_dotenv

# ----- تحميل متغيرات البيئة -----
load_dotenv()
CLIENT_FILE = os.getenv("GOOGLE_CLIENT_FILE")

# ----- إعداد صلاحيات Google -----
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ----- تحميل أو إنشاء بيانات الاعتماد -----
creds = None
if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        try:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        except FileNotFoundError:
            st.error(f"Client file '{CLIENT_FILE}' not found. Check your .env settings.")
            st.stop()
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)

client = gspread.authorize(creds)
spreadsheet = client.open("Student2")

# ----- تأكد من وجود الورقة -----
DEFAULT_HEADERS = ["ID", "Name", "Email", "Grade", "Notes"]
try:
    ws = spreadsheet.worksheet("Sheet1")
except gspread.exceptions.WorksheetNotFound:
    ws = spreadsheet.add_worksheet(title="Sheet1", rows="1000", cols=str(len(DEFAULT_HEADERS)))
    ws.insert_row(DEFAULT_HEADERS, index=1)

# ====== دوال مساعدة ======
def next_id(ws):
    values = ws.col_values(1)[1:]
    nums = [int(v) for v in values if v.isdigit()]
    return str(max(nums)+1) if nums else "1"

def add_student(ws, student):
    headers = ws.row_values(1)
    if "ID" not in student or not str(student.get("ID")).strip():
        student["ID"] = next_id(ws)
    row = [student.get(h, "") for h in headers]
    ws.append_row(row, value_input_option="USER_ENTERED")
    return student["ID"]

def add_students_batch(ws, students):
    headers = ws.row_values(1)
    all_rows = []
    values = ws.col_values(1)[1:]
    last_id = max([int(v) for v in values if v.isdigit()]+[0])
    next_id_counter = last_id + 1
    for s in students:
        if not s.get("ID"):
            s["ID"] = str(next_id_counter)
            next_id_counter += 1
        row = [s.get(h, "") for h in headers]
        all_rows.append(row)
    ws.append_rows(all_rows, value_input_option="USER_ENTERED")
    return [r[0] for r in all_rows]

def get_all_students(ws):
    try:
        return ws.get_all_records()
    except gspread.exceptions.APIError:
        st.error("Error fetching students. Check your Google Sheets connection.")
        return []

def get_student_by_id(ws, student_id):
    data = get_all_students(ws)
    for s in data:
        if str(s["ID"]) == str(student_id):
            return s
    return None

# ====== Streamlit UI ======
st.title("Student Management System")

menu = ["Add Student", "Add Batch", "View Students", "Search Student", "Update Student", "Delete Student"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Student":
    st.subheader("Add a New Student")
    name = st.text_input("Name")
    email = st.text_input("Email")
    grade = st.text_input("Grade")
    notes = st.text_area("Notes")
    if st.button("Add Student"):
        new_id = add_student(ws, {"Name": name, "Email": email, "Grade": grade, "Notes": notes})
        st.success(f"Student {name} added with ID {new_id}")

elif choice == "Add Batch":
    st.subheader("Add Multiple Students")
    st.info("Enter student data as Name,Email,Grade,Notes per line")
    text_input = st.text_area("Enter students")
    if st.button("Add Students") and text_input:
        students_list = []
        for line in text_input.strip().split('\n'):
            parts = line.split(',')
            if len(parts) >= 4:
                students_list.append({
                    "Name": parts[0].strip(),
                    "Email": parts[1].strip(),
                    "Grade": parts[2].strip(),
                    "Notes": parts[3].strip()
                })
        added_ids = add_students_batch(ws, students_list)
        st.success(f"Added {len(added_ids)} students successfully!")

elif choice == "View Students":
    st.subheader("All Students")
    students = get_all_students(ws)
    st.table(students)

elif choice == "Search Student":
    st.subheader("Search by ID")
    search_id = st.text_input("Enter Student ID")
    if st.button("Search"):
        student = get_student_by_id(ws, search_id)
        if student:
            st.json(student)
        else:
            st.warning("Student not found")

elif choice == "Update Student":
    st.subheader("Update Student Data")
    update_id = st.text_input("Enter Student ID to Update")
    if st.button("Load Student Data"):
        student = get_student_by_id(ws, update_id)
        if student:
            name = st.text_input("Name", value=student["Name"])
            email = st.text_input("Email", value=student["Email"])
            grade = st.text_input("Grade", value=student["Grade"])
            notes = st.text_area("Notes", value=student["Notes"])
            if st.button("Update Student"):
                headers = ws.row_values(1)
                all_rows = ws.get_all_values()
                row_index = None
                for idx, row in enumerate(all_rows):
                    if row and row[0] == str(update_id):
                        row_index = idx + 1
                        break
                if row_index:
                    ws.update_cell(row_index, headers.index("Name")+1, name)
                    ws.update_cell(row_index, headers.index("Email")+1, email)
                    ws.update_cell(row_index, headers.index("Grade")+1, grade)
                    ws.update_cell(row_index, headers.index("Notes")+1, notes)
                    st.success(f"Student ID {update_id} updated successfully!")
                else:
                    st.error("Student not found!")

elif choice == "Delete Student":
    st.subheader("Delete Student")
    del_id = st.text_input("Enter Student ID to Delete")
    if st.button("Delete"):
        all_rows = ws.get_all_values()
        row_index = None
        for idx, row in enumerate(all_rows):
            if row and row[0] == str(del_id):
                row_index = idx + 1
                break
        if row_index:
            ws.delete_rows(row_index)
            st.success(f"Student ID {del_id} deleted successfully!")
        else:
            st.error("Student not found!")
