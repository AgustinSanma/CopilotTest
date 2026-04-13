from src.app import activities


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_activity_count = len(activities)

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert len(payload) == expected_activity_count
    assert "Chess Club" in payload


def test_get_activities_returns_expected_fields(client):
    # Arrange
    required_fields = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")
    payload = response.json()

    # Assert
    assert response.status_code == 200
    for activity_details in payload.values():
        assert required_fields.issubset(activity_details.keys())


def test_get_activities_disables_caching(client):
    # Arrange
    expected_cache_header = "no-store"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.headers["cache-control"] == expected_cache_header