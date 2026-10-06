from .constants import BASE_URL
import pytest
import requests


@pytest.mark.smoke
@pytest.mark.parametrize("name, car", [
            ("Саша", "BMW"),
            ("Мария", "Toyota"),
        ])
def test_taxi_drivers(name, car):
    request_data = {
            "name": name,
            "car": car
        }
    result = requests.post(
            f'{BASE_URL}/drivers',
            json=request_data,
        )
    body = result.json()

    assert result.status_code == 201
    assert isinstance(body["name"], str)
    assert isinstance(body["car"], str)
    assert body["name"] == name
    assert body["car"] == car

    driver_id = body["id"]
    request_data = {
        "status": "online",
        "lat": 55.7558,
        "lon": 37.6173
        }
    result = requests.post(
            f'{BASE_URL}/drivers/status/{driver_id}',
            json=request_data,
        )
    assert result.status_code == 200
