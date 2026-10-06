from .constants import BASE_URL, USER
import uuid
import requests
import pytest


@pytest.fixture
def test_user():
    user = {'username': f'user_{uuid.uuid4().hex[:8]}', 'password': '1234'}
    registrate_response = requests.post(
        f'{BASE_URL}/auth/registrate',
        json=user
        )
    assert registrate_response.status_code == 201
    return user


@pytest.fixture
def order_fixture(test_user):
    unique = uuid.uuid4().hex[:8]
    request_data = {
                'from_address': f'Маркса {unique}',
                'to_address': f'Ватутино {unique}',
                'price': 350,
                "pickup_lat": 55.7600,
                "pickup_lon": 37.6100,
                "destination_lat": 55.7539,
                "destination_lon": 37.6208
        }
    headers = {
                "Idempotency-Key": str(uuid.uuid4())
            }
    session = requests.Session()
    login_response = session.post(f'{BASE_URL}/auth/login', json=test_user)
    assert login_response.status_code == 200

    cookie = session.cookies.get("my_cookie")

    driver = session.post(f'{BASE_URL}/drivers',
                          json={'name': 'Тест',
                                'car': 'Lada'})
    driver_id = driver.json()['id']
    status = session.post(f'{BASE_URL}/drivers/status/{driver_id}',
                          json={'status': 'online', 'lat': 55.76, 'lon': 37.61}
                          )
    assert status.status_code == 200

    pay_response = session.post(
        f'{BASE_URL}/pay/top-up',
        json={"money": 1000.00},
        cookies={"my_cookie": cookie}
    )

    if pay_response.status_code != 200:
        print(f"ОШИБКА ПОПОЛНЕНИЯ: {pay_response.json()}")

    assert pay_response.status_code == 200

    result = session.post(
            f'{BASE_URL}/taxi',
            json=request_data,
            headers=headers,
            cookies={"my_cookie": cookie}
        )

    return {
        'response': result,
        'request_data': request_data,
        'headers': headers,
        'cookies': cookie,
        'session': session
        }
