import pytest
from urllib.parse import quote

from src.app import activities


def test_signup_adds_new_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name, safe='')}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name, safe='')}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name, safe='')}/signup", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 400
    assert payload == {"detail": "Student already signed up for this activity"}


@pytest.mark.parametrize("activity_name", list(activities.keys()))
def test_signup_rejects_activity_at_capacity(client, activity_name):
    # Arrange
    max_participants = activities[activity_name]["max_participants"]
    activities[activity_name]["participants"] = [
        f"student{index}@mergington.edu" for index in range(max_participants)
    ]
    email = "overflow.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name, safe='')}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}


def test_signup_normalizes_email_case(client):
    # Arrange
    activity_name = "Chess Club"
    email_mixed = "New.Student@Mergington.EDU"
    email_normalized = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name, safe='')}/signup", params={"email": email_mixed})

    # Assert
    assert response.status_code == 200
    assert email_normalized in activities[activity_name]["participants"]


def test_signup_normalizes_email_whitespace(client):
    # Arrange
    activity_name = "Chess Club"
    email_with_spaces = "  new.student@mergington.edu  "
    email_normalized = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{quote(activity_name, safe='')}/signup", params={"email": email_with_spaces})

    # Assert
    assert response.status_code == 200
    assert email_normalized in activities[activity_name]["participants"]


@pytest.mark.parametrize("invalid_email", [
    "not-an-email",
    "missing@",
    "@nodomain.com",
    "double..dot@example.com",
    "user@.example.com",
    "",
])
def test_signup_rejects_invalid_email(client, invalid_email):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{quote(activity_name, safe='')}/signup", params={"email": invalid_email})

    # Assert
    assert response.status_code == 400