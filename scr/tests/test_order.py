from decimal import Decimal

from .constants import BASE_URL


def test_ordering_a_taxi(order_fixture):
    response = order_fixture['response']
    request_data = order_fixture['request_data']

    body = response.json()
    assert response.status_code == 201
    assert isinstance(body["from_address"], str)
    assert isinstance(body["to_address"], str)
    assert Decimal(body['price']) == Decimal(str(request_data['price']))
    assert body['to_address'] == request_data['to_address']
    assert body['from_address'] == request_data['from_address']


def test_order_search(order_fixture):
    response = order_fixture['response']
    cookie = order_fixture['cookies']
    session = order_fixture['session']

    order_id = response.json()["id"]

    result = session.get(f'{BASE_URL}/taxi/{order_id}',
                         cookies={"my_cookie": cookie}
                         )
    assert result.status_code == 200

    order_id = 1000000
    result = session.get(f'{BASE_URL}/taxi/{order_id}',
                         cookies={"my_cookie": cookie}
                         )
    assert result.status_code == 404


def test_idempotency(order_fixture):
    headers = order_fixture['headers']
    request_data = order_fixture['request_data']
    cookie = order_fixture['cookies']
    session = order_fixture['session']

    responce_one = session.post(
                    f'{BASE_URL}/taxi',
                    json=request_data,
                    headers=headers,
                    cookies={"my_cookie": cookie}
                )
    responce_one_id = responce_one.json()['id']
    assert responce_one.status_code == 201

    responce_two = session.post(
            f'{BASE_URL}/taxi',
            json=request_data,
            headers=headers,
            cookies={"my_cookie": cookie}
            )
    responce_two_id = responce_two.json()['id']
    assert responce_two.status_code == 201
    assert responce_one_id == responce_two_id


def test_order_delete(order_fixture):
    response = order_fixture['response']
    cookie = order_fixture['cookies']
    session = order_fixture['session']

    order_id = response.json()["id"]

    result = session.delete(f'{BASE_URL}/taxi/{order_id}',
                            cookies={"my_cookie": cookie}
                            )
    assert result.status_code == 204

    result = session.get(f'{BASE_URL}/taxi/{order_id}',
                         cookies={"my_cookie": cookie}
                         )
    assert result.status_code == 404
