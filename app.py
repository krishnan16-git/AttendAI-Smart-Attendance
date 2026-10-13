import os
from datetime import date, datetime
from functools import wraps

import cv2
import numpy as np
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///attendai.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    student_code = db.Column(db.String(30), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True)
    department = db.Column(db.String(80), nullable=False)
    class_name = db.Column(db.String(80), nullable=False)
    face_image = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Attendance(db.Model):
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False, default=date.today)
    attendance_time = db.Column(db.Time, nullable=False, default=datetime.now().time)
    status = db.Column(db.String(20), nullable=False, default="Present")
    method = db.Column(db.String(30), nullable=False, default="Face Recognition")
    student = db.relationship("Student", backref="attendance_records")
    __table_args__ = (db.UniqueConstraint("student_id", "attendance_date", name="uq_student_day"),)

@app.get("/")
def dashboard():
    today = date.today()
    total = Student.query.count()
    present = Attendance.query.filter_by(attendance_date=today, status="Present").count()
    recent = Attendance.query.order_by(Attendance.id.desc()).limit(8).all()
    return render_template("dashboard.html", total=total, present=present,
                           absent=max(total-present, 0),
                           attendance_rate=round(present * 100 / total) if total else 0,
                           recent=recent, today=today)

@app.get("/students")
def students_page():
    return render_template("students.html", students=Student.query.order_by(Student.full_name).all())

@app.post("/api/students")
def add_student():
    data = request.get_json(silent=True) or request.form
    code = (data.get("student_code") or "").strip()
    name = (data.get("full_name") or "").strip()
    department = (data.get("department") or "").strip()
    class_name = (data.get("class_name") or "").strip()
    email = (data.get("email") or "").strip() or None
    if not all([code, name, department, class_name]):
        return jsonify(error="Student ID, name, department, and class are required."), 400
    student = Student(student_code=code, full_name=name, email=email,
                      department=department, class_name=class_name)
    db.session.add(student)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Student ID or email already exists."), 409
    return jsonify(message="Student added successfully.", id=student.id), 201

@app.post("/api/attendance")
def mark_attendance():
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    student = db.session.get(Student, student_id) if student_id else None
    if not student:
        return jsonify(error="Choose a valid student."), 404
    record = Attendance(student_id=student.id, attendance_date=date.today(),
                        attendance_time=datetime.now().time().replace(microsecond=0),
                        status="Present", method=data.get("method", "Manual Demo"))
    db.session.add(record)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Attendance has already been marked for this student today."), 409
    return jsonify(message=f"Attendance marked for {student.full_name}.", time=record.attendance_time.strftime("%H:%M:%S"))

@app.get("/api/students")
def students_api():
    return jsonify([{"id": s.id, "student_code": s.student_code, "full_name": s.full_name,
                     "department": s.department, "class_name": s.class_name}
                    for s in Student.query.order_by(Student.full_name).all()])

@app.get("/api/attendance/today")
def today_attendance():
    rows = Attendance.query.filter_by(attendance_date=date.today()).order_by(Attendance.id.desc()).all()
    return jsonify([{"name": r.student.full_name, "student_code": r.student.student_code,
                     "time": r.attendance_time.strftime("%H:%M:%S"), "status": r.status,
                     "method": r.method} for r in rows])

@app.get("/reports")
def reports():
    records = Attendance.query.order_by(Attendance.attendance_date.desc(), Attendance.id.desc()).limit(300).all()
    return render_template("reports.html", records=records)

@app.get("/face-recognition")
def face_page():
    return render_template("face.html", students=Student.query.order_by(Student.full_name).all())

@app.post("/api/face/recognize")
def face_recognize():
    """
    Demo face matcher: compare a submitted camera frame against saved face images
    using OpenCV LBPH if opencv-contrib-python is installed and trained data exists.
    For the beginner starter project, this endpoint returns guidance until a model
    has been trained. Do not use this demo as a security-grade identity system.
    """
    return jsonify(error="Face recognition setup is not trained yet. First register face images and train the model; use the demo attendance button while learning."), 501

@app.get("/setup-db")
def setup_db():
    # Convenient for local learning only. In a deployed app, use migrations instead.
    db.create_all()
    return "Database tables created. Remove or protect this route before deployment."

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
