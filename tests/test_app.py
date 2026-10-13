import uuid
import pytest

from app import app, db, Student, Attendance


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield client


@pytest.fixture
def test_student(client):
    code = f"TEST-{uuid.uuid4().hex[:8]}"
    student_id = None

    with app.app_context():
        student = Student(
            student_code=code,
            full_name="Pytest Student",
            email=f"{code}@example.com",
            department="Computer Science",
            class_name="3rd Year",
        )
        db.session.add(student)
        db.session.commit()
        student_id = student.id

    yield {"id": student_id, "code": code}

    with app.app_context():
        Attendance.query.filter_by(
            student_id=student_id
        ).delete()

        student = db.session.get(Student, student_id)

        if student:
            db.session.delete(student)

        db.session.commit()


def test_dashboard_loads(client):
    response = client.get("/")
    assert response.status_code == 200


def test_students_page_loads(client):
    response = client.get("/students")
    assert response.status_code == 200


def test_face_page_loads(client):
    response = client.get("/face-recognition")
    assert response.status_code == 200


def test_reports_page_loads(client):
    response = client.get("/reports")
    assert response.status_code == 200


def test_student_registration(client):
    code = f"NEW-{uuid.uuid4().hex[:8]}"

    response = client.post(
        "/api/students",
        json={
            "student_code": code,
            "full_name": "New Test Student",
            "email": f"{code}@example.com",
            "department": "Computer Science",
            "class_name": "3rd Year",
        },
    )

    assert response.status_code == 201

    student_id = response.get_json()["id"]

    with app.app_context():
        student = db.session.get(Student, student_id)
        assert student is not None

        Attendance.query.filter_by(
            student_id=student_id
        ).delete()

        db.session.delete(student)
        db.session.commit()


def test_duplicate_student_id_rejected(client, test_student):
    response = client.post(
        "/api/students",
        json={
            "student_code": test_student["code"],
            "full_name": "Duplicate Student",
            "department": "Computer Science",
            "class_name": "3rd Year",
        },
    )

    assert response.status_code == 409


def test_attendance_can_be_marked(client, test_student):
    response = client.post(
        "/api/attendance",
        json={
            "student_id": test_student["id"],
            "method": "Manual Demo",
        },
    )

    assert response.status_code == 200


def test_duplicate_attendance_rejected(client, test_student):
    first = client.post(
        "/api/attendance",
        json={"student_id": test_student["id"]},
    )

    second = client.post(
        "/api/attendance",
        json={"student_id": test_student["id"]},
    )

    assert first.status_code == 200
    assert second.status_code == 409


def test_invalid_student_rejected(client):
    response = client.post(
        "/api/attendance",
        json={"student_id": 999999999},
    )

    assert response.status_code == 404


def test_today_attendance_api(client, test_student):
    client.post(
        "/api/attendance",
        json={"student_id": test_student["id"]},
    )

    response = client.get("/api/attendance/today")

    assert response.status_code == 200

    records = response.get_json()

    assert any(
        record["student_code"] == test_student["code"]
        for record in records
    )