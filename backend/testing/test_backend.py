import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from datetime import datetime
from core.config import SQLALCHEMY_TEST_DATABASE_URL


engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture()
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


user_data = {"email": "test@test.com", "username": "testuser", "password": "testpass"}
project_data = {"title": "Test Project", "description": "This is a test project"}
task_data = {
    "title": "Test Task",
    "description": "This is a test task",
    "status": "IN_PROGRESS",
    "deadline": "2023-05-10T17:35",
}


def create_user(client, user_data=user_data):
    response = client.post("/user/create/", json=user_data)
    return response


def login(client, user_data=user_data):
    auth_response = client.post(
        "/user/login/",
        data={"username": user_data["email"], "password": user_data["password"]},
    )
    assert auth_response.status_code == 200
    token = auth_response.json()["access_token"]
    return token


def create_project(client, token, project_data=project_data):
    response = client.post(
        "/project/create/",
        json=project_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    return response


def create_task(client, project_id, token, task_data=task_data):
    response = client.post(
        f"/project/{project_id}/task/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    return response


def test_create_user(client):
    response = create_user(client)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]
    assert response.json()["username"] == user_data["username"]
    assert "hashed_password" not in response.json()


def test_create_project(client):
    user_response = create_user(client)
    assert user_response.status_code == 200

    token = login(client)
    project_response = create_project(client, token)
    assert project_response.status_code == 200
    assert project_response.json()["title"] == project_data["title"]
    assert project_response.json()["description"] == project_data["description"]
    assert project_response.json()["creator_id"] == user_response.json()["id"]
    assert project_response.json()["users"][0] == user_response.json()
    assert project_response.json()["managers"][0] == user_response.json()


def test_add_user_to_project(client):
    user_response = create_user(client)
    assert user_response.status_code == 200

    user2_data = {
        "email": "test2@test.com",
        "username": "testuser2",
        "password": "testpass",
    }
    user2_response = create_user(client, user2_data)
    assert user2_response.status_code == 200

    token = login(client)

    project_response = create_project(client, token)
    assert project_response.status_code == 200
    project_id = project_response.json()["id"]
    response = client.put(
        f"/project/{project_id}/add/user",
        params={"email_to_add": user2_data["email"]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["users"] == [user_response.json(), user2_response.json()]


def test_create_task(client):
    user_response = create_user(client)
    assert user_response.status_code == 200
    token = login(client)
    project_response = create_project(client, token)
    assert project_response.status_code == 200
    task_response = create_task(client, project_response.json()["id"], token)
    assert task_response.status_code == 200
    assert task_response.json()["title"] == task_data["title"]
    assert task_response.json()["description"] == task_data["description"]
    assert datetime.fromisoformat(task_response.json()["deadline"]).strftime("%d-%m-%Y %H:%M") == datetime.fromisoformat(task_data["deadline"]).strftime("%d-%m-%Y %H:%M")
    assert task_response.json()["status"] == task_data["status"]
    assert task_response.json()["project_id"] == project_response.json()["id"]
    assert task_response.json()["created_by_id"] == user_response.json()["id"]
    assert task_response.json()["assignee_id"] is None
