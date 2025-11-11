# Student Management System with Google Sheets and Streamlit

## Project Description

This Python project allows you to manage student data directly via Google Sheets using a simple web interface with Streamlit.  
You can add students, edit their data, search for them, and delete them easily without manually handling the spreadsheet.

---

## Main Features

1. **Add a Single Student**
   - Automatically generates an ID if not provided.
   - Adds the student with all details in a new row.

2. **Add Multiple Students (Batch)**
   - Allows adding a list of students at once.
   - Automatically generates IDs for each student.

3. **View All Students**
   - Displays all student data in a well-formatted table.

4. **Search Student**
   - Search for a student by ID.
   - Displays all their details.

5. **Update Student**
   - Edit any field of a student directly from the interface.

6. **Delete Student**
   - Remove a student from the sheet using their ID.

7. **Simple Web Interface (Streamlit)**
   - Easy-to-use web interface running in the browser.

---

## Requirements

- Python >= 3.8
- Libraries:
```bash
pip install gspread google-auth google-auth-oauthlib streamlit
