import os
import csv
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ----------------------------
# Constants
# ----------------------------
DATABASE = "database.db"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------------------
# Helper Functions
# ----------------------------
def safe_int(value):
    try:
        return int(value)
    except:
        return 0

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idno TEXT,
            name TEXT,
            branch TEXT,
            year TEXT,
            semester TEXT,
            subject TEXT,
            subject_code TEXT,
            type TEXT,
            oclass TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # Initialize DB on startup

# ----------------------------
# Admin Credentials
# ----------------------------
ADMIN_USERNAME = "rushitha"
ADMIN_PASSWORD = "rushi123"

# ----------------------------
# Routes
# ----------------------------

# Home / login page
@app.route("/")
def index():
    return render_template("index.html")

# Admin login page
@app.route("/admin_login_page")
def admin_login_page():
    return render_template("admin_login.html")

# Admin login processing
@app.route("/admin_login", methods=["POST"])
def admin_login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session["admin"] = True
        return redirect(url_for("admin"))
    else:
        flash("Invalid username or password", "error")
        return redirect(url_for("admin_login_page"))

# Admin dashboard
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("admin_login_page"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    conn.close()

    return render_template("admin.html", students=students)

# Admin logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# Upload CSV
@app.route("/upload_students", methods=["POST"])
def upload_students():
    if not session.get("admin"):
        return redirect(url_for("admin_login_page"))

    if "file" not in request.files:
        flash("Upload failed", "error")
        return redirect(url_for("admin"))

    file = request.files["file"]
    if file.filename == "":
        flash("Upload failed", "error")
        return redirect(url_for("admin"))

    if file and allowed_file(file.filename):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        try:
            conn = get_db()
            cur = conn.cursor()

            # Robust CSV reading with multiple encoding attempts
            try:
                with open(filepath, "r", encoding="utf-8-sig") as csvfile:
                    reader = csv.DictReader(csvfile)
                    rows = list(reader)
            except UnicodeDecodeError:
                with open(filepath, "r", encoding="latin-1") as csvfile:
                    reader = csv.DictReader(csvfile)
                    rows = list(reader)

            count = 0
            for row in rows:
                # Use the exact column names from your CSV
                idno = row.get("id", "")
                branch = row.get("branch", "")
                year = row.get("year", "")
                semester = row.get("sem", "")
                subject = row.get("sub", "")
                subject_code = row.get("subjectcode", "")
                type_val = row.get("type", "")
                oclass = row.get("oclass", "")

                # Insert into database
                cur.execute("""
                    INSERT INTO students 
                    (idno, name, branch, year, semester, subject, subject_code, type, oclass)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    idno.strip() if idno and idno.strip() else None,
                    "",  # Empty name as requested
                    branch.strip() if branch and branch.strip() else None,
                    year.strip() if year and year.strip() else None,
                    semester.strip() if semester and semester.strip() else None,
                    subject.strip() if subject and subject.strip() else None,
                    subject_code.strip() if subject_code and subject_code.strip() else None,
                    type_val.strip() if type_val and type_val.strip() else None,
                    oclass.strip() if oclass and oclass.strip() else None
                ))
                count += 1

            conn.commit()
            conn.close()
            flash(f"Students uploaded successfully! Total records: {count}", "success")
            return redirect(url_for("admin"))

        except Exception as e:
            flash("Upload failed", "error")
            return redirect(url_for("admin"))

    flash("Upload failed", "error")
    return redirect(url_for("admin"))

# Delete student
@app.route("/delete_student/<idno>")
def delete_student(idno):
    if not session.get("admin"):
        return redirect(url_for("admin_login_page"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE idno = ?", (idno,))
    conn.commit()
    conn.close()

    flash("Student deleted successfully", "success")
    return redirect(url_for("admin"))

# Delete entire database (old data)
@app.route("/delete_db")
def delete_db():
    if not session.get("admin"):
        return redirect(url_for("admin_login_page"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students")
    conn.commit()
    conn.close()

    flash("All student data deleted successfully!", "success")
    return redirect(url_for("admin"))

# Student login
@app.route("/student_login", methods=["POST"])
def student_login():
    idno = request.form.get("idno")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE idno=?", (idno,))
    rows = cur.fetchall()
    conn.close()

    if rows:
        return render_template("student.html", student_data=rows, student_id=idno)
    else:
        flash("No data found for given ID Number", "error")
        return redirect(url_for("index"))

# Run Flask
if __name__ == "__main__":
    app.run(debug=True)