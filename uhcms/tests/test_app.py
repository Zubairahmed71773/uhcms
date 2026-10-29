import pytest
from app import create_app, validate_complaint

@pytest.fixture
def client(tmp_path):
    return create_app(str(tmp_path / "test.db")).test_client()

def login(c, email, pw):
    return c.post("/login", data={"email": email, "password": pw}, follow_redirects=True)

def student(c):
    c.post("/register", data={"name": "Ali", "email": "ali@uni.edu", "password": "secret1"})
    login(c, "ali@uni.edu", "secret1")

GOOD = {"title": "Projector broken", "category": "Classroom Equipment", "description": "Lab 3 projector off"}

def test_validate_reports_missing_title():          # TC-04
    assert "title" in validate_complaint({**GOOD, "title": ""})

def test_wrong_password(client):                    # TC-02
    assert b"Wrong email or password" in login(client, "x@uni.edu", "nope").data

def test_valid_complaint_gets_id(client):           # TC-03
    student(client)
    r = client.post("/complaints/new", data=GOOD, follow_redirects=True)
    assert b"CMP-001" in r.data

def test_empty_description_rejected(client):        # TC-04
    student(client)
    r = client.post("/complaints/new", data={**GOOD, "description": ""}, follow_redirects=True)
    assert b"Please fill in" in r.data

def test_student_cannot_change_status(client):      # security
    student(client)
    client.post("/complaints/new", data=GOOD)
    assert client.post("/complaints/1/status", data={"status": "Closed"}).status_code == 403

def test_staff_updates_status_student_sees_it(client):  # TC-05, TC-06
    student(client)
    client.post("/complaints/new", data=GOOD)
    client.get("/logout")
    login(client, "staff@uni.edu", "staff123")
    client.post("/complaints/1/status", data={"status": "In Progress"})
    client.get("/logout")
    login(client, "ali@uni.edu", "secret1")
    assert b"In Progress" in client.get("/complaints/1").data

def test_public_pages_load(client):
    assert b"Campus Helpdesk" in client.get("/").data
    assert b"Muhammad Zubair" in client.get("/about").data

def test_forgot_and_dashboard(client):
    assert b"Reset your password" in client.get("/forgot").data
    student(client)
    assert b"Quick actions" in client.get("/dashboard").data
