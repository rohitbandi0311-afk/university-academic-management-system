import os
from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# =========================================================
# MYSQL DATABASE CONNECTION
# =========================================================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("MYSQL_PASSWORD"),
    database="university_db"
)



# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def home():

    cursor = db.cursor()

    counts = {}

    tables = [
        "college",
        "department",
        "student",
        "faculty",
        "course",
        "enrollment"
    ]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cursor.fetchone()[0]

    cursor.close()

    return render_template(
        "dashboard.html",
        counts=counts
    )


# =========================================================
# STUDENTS - VIEW
# =========================================================

@app.route("/students")
def students():

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            s.student_id,
            s.name,
            s.gender,
            s.dob,
            s.email,
            d.dept_name
        FROM student s
        INNER JOIN department d
            ON s.dept_id = d.dept_id
        ORDER BY s.student_id
    """)

    students = cursor.fetchall()

    cursor.close()

    return render_template(
        "students.html",
        students=students
    )


# =========================================================
# STUDENTS - ADD
# =========================================================

@app.route("/students/add", methods=["GET", "POST"])
def add_student():

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        student_id = request.form["student_id"]
        name = request.form["name"]
        gender = request.form["gender"]
        dob = request.form["dob"]
        email = request.form["email"]
        dept_id = request.form["dept_id"]

        cursor.execute("""
            INSERT INTO student
            (
                student_id,
                name,
                gender,
                dob,
                email,
                dept_id
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            student_id,
            name,
            gender,
            dob,
            email,
            dept_id
        ))

        db.commit()

        cursor.close()

        return redirect("/students")

    cursor.execute("""
        SELECT
            dept_id,
            dept_name
        FROM department
        ORDER BY dept_id
    """)

    departments = cursor.fetchall()

    cursor.close()

    return render_template(
        "student_form.html",
        departments=departments
    )


# =========================================================
# STUDENTS - EDIT
# =========================================================

@app.route("/students/edit/<student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form["name"]
        gender = request.form["gender"]
        dob = request.form["dob"]
        email = request.form["email"]
        dept_id = request.form["dept_id"]

        cursor.execute("""
            UPDATE student
            SET
                name = %s,
                gender = %s,
                dob = %s,
                email = %s,
                dept_id = %s
            WHERE student_id = %s
        """, (
            name,
            gender,
            dob,
            email,
            dept_id,
            student_id
        ))

        db.commit()

        cursor.close()

        return redirect("/students")

    cursor.execute("""
        SELECT
            student_id,
            name,
            gender,
            dob,
            email,
            dept_id
        FROM student
        WHERE student_id = %s
    """, (student_id,))

    student = cursor.fetchone()

    cursor.execute("""
        SELECT
            dept_id,
            dept_name
        FROM department
        ORDER BY dept_id
    """)

    departments = cursor.fetchall()

    cursor.close()

    return render_template(
        "edit_student.html",
        student=student,
        departments=departments
    )


# =========================================================
# STUDENTS - DELETE
# =========================================================

@app.route("/students/delete/<student_id>", methods=["POST"])
def delete_student(student_id):

    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM student
        WHERE student_id = %s
    """, (student_id,))

    db.commit()

    cursor.close()

    return redirect("/students")


# =========================================================
# REPORTS
# =========================================================

@app.route("/reports")
def reports():

    cursor = db.cursor(dictionary=True)

    # -----------------------------------------------------
    # 1. TOTAL STUDENTS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*) AS total_students
        FROM student
    """)

    total_students = cursor.fetchone()["total_students"]


    # -----------------------------------------------------
    # 2. STUDENTS WITH DEPARTMENTS
    # INNER JOIN
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            s.student_id,
            s.name,
            d.dept_name
        FROM student s
        INNER JOIN department d
            ON s.dept_id = d.dept_id
        ORDER BY s.student_id
    """)

    student_departments = cursor.fetchall()


    # -----------------------------------------------------
    # 3. STUDENTS BY DEPARTMENT
    # GROUP BY + COUNT
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            d.dept_name,
            COUNT(s.student_id) AS student_count
        FROM department d
        LEFT JOIN student s
            ON d.dept_id = s.dept_id
        GROUP BY
            d.dept_id,
            d.dept_name
        ORDER BY d.dept_id
    """)

    department_counts = cursor.fetchall()


    # -----------------------------------------------------
    # 4. COURSE DETAILS
    # INNER JOIN
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            c.course_id,
            c.title,
            d.dept_name,
            c.credits
        FROM course c
        INNER JOIN department d
            ON c.dept_id = d.dept_id
        ORDER BY c.course_id
    """)

    courses = cursor.fetchall()


    # Close cursor
    cursor.close()


    return render_template(
        "reports.html",
        total_students=total_students,
        student_departments=student_departments,
        department_counts=department_counts,
        courses=courses
    )


# =========================================================
# RUN APPLICATION
# =========================================================
@app.route("/departments")
def departments():

    cursor = db.cursor()

    cursor.execute("""
        SELECT dept_id, dept_name, college_id
        FROM department
        ORDER BY dept_id
    """)

    departments = cursor.fetchall()

    cursor.close()

    return render_template(
        "departments.html",
        departments=departments
    )
@app.route("/departments/add", methods=["GET", "POST"])
def add_department():

    cursor = db.cursor()

    if request.method == "POST":

        dept_id = request.form["dept_id"]
        dept_name = request.form["dept_name"]
        college_id = request.form["college_id"]

        cursor.execute("""
            INSERT INTO department
            (dept_id, dept_name, college_id)
            VALUES (%s, %s, %s)
        """, (dept_id, dept_name, college_id))

        db.commit()

        cursor.close()

        return redirect("/departments")

    cursor.execute("""
        SELECT college_id, name
        FROM college
        ORDER BY college_id
    """)

    colleges = cursor.fetchall()

    cursor.close()

    return render_template(
        "department_form.html",
        colleges=colleges
    )
@app.route("/departments/edit/<int:dept_id>", methods=["GET", "POST"])
def edit_department(dept_id):

    cursor = db.cursor()

    if request.method == "POST":

        dept_name = request.form["dept_name"]
        college_id = request.form["college_id"]

        cursor.execute("""
            UPDATE department
            SET dept_name = %s,
                college_id = %s
            WHERE dept_id = %s
        """, (dept_name, college_id, dept_id))

        db.commit()

        cursor.close()

        return redirect("/departments")

    cursor.execute("""
        SELECT dept_id, dept_name, college_id
        FROM department
        WHERE dept_id = %s
    """, (dept_id,))

    department = cursor.fetchone()

    cursor.execute("""
        SELECT college_id, name
        FROM college
        ORDER BY college_id
    """)

    colleges = cursor.fetchall()

    cursor.close()

    return render_template(
        "edit_department.html",
        department=department,
        colleges=colleges
    )
@app.route("/departments/delete/<int:dept_id>")
def delete_department(dept_id):

    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM department
        WHERE dept_id = %s
    """, (dept_id,))

    db.commit()

    cursor.close()

    return redirect("/departments")
@app.route("/faculty")
def faculty():

    cursor = db.cursor()

    cursor.execute("""
        SELECT faculty_id,
               name,
               qualification,
               dept_id,
               email
        FROM faculty
        ORDER BY faculty_id
    """)

    faculties = cursor.fetchall()

    cursor.close()

    return render_template(
        "faculty.html",
        faculties=faculties
    )
@app.route("/faculty/add", methods=["GET", "POST"])
def add_faculty():

    cursor = db.cursor()

    if request.method == "POST":

        faculty_id = request.form["faculty_id"]
        name = request.form["name"]
        qualification = request.form["qualification"]
        dept_id = request.form["dept_id"]
        email = request.form["email"]

        cursor.execute("""
            INSERT INTO faculty
            (
                faculty_id,
                name,
                qualification,
                dept_id,
                email
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            faculty_id,
            name,
            qualification,
            dept_id,
            email
        ))

        db.commit()

        cursor.close()

        return redirect("/faculty")

    cursor.execute("""
        SELECT dept_id, dept_name
        FROM department
        ORDER BY dept_id
    """)

    departments = cursor.fetchall()

    cursor.close()

    return render_template(
        "faculty_form.html",
        departments=departments
    )
@app.route("/faculty/edit/<faculty_id>", methods=["GET", "POST"])
def edit_faculty(faculty_id):

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form["name"]
        qualification = request.form["qualification"]
        dept_id = request.form["dept_id"]
        email = request.form["email"]

        cursor.execute("""
            UPDATE faculty
            SET
                name = %s,
                qualification = %s,
                dept_id = %s,
                email = %s
            WHERE faculty_id = %s
        """, (
            name,
            qualification,
            dept_id,
            email,
            faculty_id
        ))

        db.commit()

        cursor.close()

        return redirect("/faculty")

    cursor.execute("""
        SELECT
            faculty_id,
            name,
            qualification,
            dept_id,
            email
        FROM faculty
        WHERE faculty_id = %s
    """, (faculty_id,))

    faculty = cursor.fetchone()

    cursor.execute("""
        SELECT
            dept_id,
            dept_name
        FROM department
        ORDER BY dept_id
    """)

    departments = cursor.fetchall()

    cursor.close()

    return render_template(
        "edit_faculty.html",
        faculty=faculty,
        departments=departments
    )
@app.route("/faculty/delete/<faculty_id>")
def delete_faculty(faculty_id):

    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM faculty
        WHERE faculty_id = %s
    """, (faculty_id,))

    db.commit()

    cursor.close()

    return redirect("/faculty")
@app.route("/courses")
def courses():

    cursor = db.cursor()

    cursor.execute("""
        SELECT
            c.course_id,
            c.title,
            c.dept_id,
            d.dept_name,
            c.credits
        FROM course c
        INNER JOIN department d
            ON c.dept_id = d.dept_id
        ORDER BY c.course_id
    """)

    courses = cursor.fetchall()

    cursor.close()

    return render_template(
        "courses.html",
        courses=courses
    )
@app.route("/courses/add", methods=["GET", "POST"])
def add_course():

    cursor = db.cursor()

    if request.method == "POST":

        course_id = request.form["course_id"]
        title = request.form["title"]
        dept_id = request.form["dept_id"]
        credits = request.form["credits"]

        cursor.execute("""
            INSERT INTO course
            (
                course_id,
                title,
                dept_id,
                credits
            )
            VALUES (%s, %s, %s, %s)
        """, (
            course_id,
            title,
            dept_id,
            credits
        ))

        db.commit()

        cursor.close()

        return redirect("/courses")

    cursor.execute("""
        SELECT dept_id, dept_name
        FROM department
        ORDER BY dept_id
    """)

    departments = cursor.fetchall()

    cursor.close()

    return render_template(
        "course_form.html",
        departments=departments
    )
@app.route("/courses/edit/<course_id>", methods=["GET", "POST"])
def edit_course(course_id):

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        title = request.form["title"]
        dept_id = request.form["dept_id"]
        credits = request.form["credits"]

        cursor.execute("""
            UPDATE course
            SET
                title = %s,
                dept_id = %s,
                credits = %s
            WHERE course_id = %s
        """, (
            title,
            dept_id,
            credits,
            course_id
        ))

        db.commit()

        cursor.close()

        return redirect("/courses")

    cursor.execute("""
        SELECT
            course_id,
            title,
            dept_id,
            credits
        FROM course
        WHERE course_id = %s
    """, (course_id,))

    course = cursor.fetchone()

    cursor.execute("""
        SELECT
            dept_id,
            dept_name
        FROM department
        ORDER BY dept_id
    """)

    departments = cursor.fetchall()

    cursor.close()

    return render_template(
        "edit_course.html",
        course=course,
        departments=departments
    )
@app.route("/courses/delete/<course_id>")
def delete_course(course_id):

    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM course
        WHERE course_id = %s
    """, (course_id,))

    db.commit()

    cursor.close()

    return redirect("/courses")
@app.route("/enrollments")
def enrollments():

    cursor = db.cursor()

    cursor.execute("""
        SELECT
            e.enrollment_id,
            e.student_id,
            s.name,
            e.course_id,
            c.title,
            e.semester,
            e.grade
        FROM enrollment e
        INNER JOIN student s
            ON e.student_id = s.student_id
        INNER JOIN course c
            ON e.course_id = c.course_id
        ORDER BY e.enrollment_id
    """)

    enrollments = cursor.fetchall()

    cursor.close()

    return render_template(
        "enrollments.html",
        enrollments=enrollments
    )
@app.route("/enrollments/add", methods=["GET", "POST"])
def add_enrollment():

    cursor = db.cursor()

    if request.method == "POST":

        enrollment_id = request.form["enrollment_id"]
        student_id = request.form["student_id"]
        course_id = request.form["course_id"]
        semester = request.form["semester"]
        grade = request.form["grade"]

        cursor.execute("""
            INSERT INTO enrollment
            (
                enrollment_id,
                student_id,
                course_id,
                semester,
                grade
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            enrollment_id,
            student_id,
            course_id,
            semester,
            grade
        ))

        db.commit()

        cursor.close()

        return redirect("/enrollments")

    cursor.execute("""
        SELECT student_id, name
        FROM student
        ORDER BY student_id
    """)

    students = cursor.fetchall()

    cursor.execute("""
        SELECT course_id, title
        FROM course
        ORDER BY course_id
    """)

    courses = cursor.fetchall()

    cursor.close()

    return render_template(
        "enrollment_form.html",
        students=students,
        courses=courses
    )
@app.route("/enrollments/edit/<enrollment_id>", methods=["GET", "POST"])
def edit_enrollment(enrollment_id):

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        student_id = request.form["student_id"]
        course_id = request.form["course_id"]
        semester = request.form["semester"]
        grade = request.form["grade"]

        cursor.execute("""
            UPDATE enrollment
            SET
                student_id = %s,
                course_id = %s,
                semester = %s,
                grade = %s
            WHERE enrollment_id = %s
        """, (
            student_id,
            course_id,
            semester,
            grade,
            enrollment_id
        ))

        db.commit()

        cursor.close()

        return redirect("/enrollments")

    cursor.execute("""
        SELECT
            enrollment_id,
            student_id,
            course_id,
            semester,
            grade
        FROM enrollment
        WHERE enrollment_id = %s
    """, (enrollment_id,))

    enrollment = cursor.fetchone()

    cursor.execute("""
        SELECT student_id, name
        FROM student
        ORDER BY student_id
    """)

    students = cursor.fetchall()

    cursor.execute("""
        SELECT course_id, title
        FROM course
        ORDER BY course_id
    """)

    courses = cursor.fetchall()

    cursor.close()

    return render_template(
        "edit_enrollment.html",
        enrollment=enrollment,
        students=students,
        courses=courses
    )
@app.route("/enrollments/delete/<enrollment_id>")
def delete_enrollment(enrollment_id):

    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM enrollment
        WHERE enrollment_id = %s
    """, (enrollment_id,))

    db.commit()

    cursor.close()

    return redirect("/enrollments")
if __name__ == "__main__":
    app.run(debug=True)