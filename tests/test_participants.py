import pytest

from src.app import activities


def test_unregister_removes_existing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload == {"detail": "Activity not found"}


def test_unregister_rejects_participant_not_registered(client):
    # Arrange
    activity_name = "Chess Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload == {"detail": "Student is not signed up for this activity"}


def test_unregister_normalizes_email_case(client):
    # Arrange - michael@mergington.edu is pre-seeded in Chess Club
    activity_name = "Chess Club"
    email_mixed = "Michael@Mergington.EDU"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email_mixed})

    # Assert
    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities[activity_name]["participants"]


def test_unregister_normalizes_email_whitespace(client):
    # Arrange - michael@mergington.edu is pre-seeded in Chess Club
    activity_name = "Chess Club"
    email_with_spaces = "  michael@mergington.edu  "

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email_with_spaces})

    # Assert
    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities[activity_name]["participants"]


@pytest.mark.parametrize("invalid_email", [
    "not-an-email",
    "missing@",
    "@nodomain.com",
    "double..dot@example.com",
    "user@.example.com",
    "",
])
def test_unregister_rejects_invalid_email(client, invalid_email):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": invalid_email})

    # Assert
    assert response.status_code == 400