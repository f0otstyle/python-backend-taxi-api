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
    body = responce_one.json()
    responce_one_id = body['id']
    assert responce_one.status_code == 201

    responce_two = session.post(
            f'{BASE_URL}/taxi',
            json=request_data,
            headers=headers,
            cookies={"my_cookie": cookie}
            )
    body = responce_two.json()
    responce_two_id = body['id']
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


def test_start_and_finish(order_fixture):
    response = order_fixture['response']
    cookie = order_fixture['cookies']
    session = order_fixture['session']

    order_id = response.json()["id"]

    offer_order = session.get(f'{BASE_URL}/taxi/offers/order/{order_id}',
                              cookies={"my_cookie": cookie})

    assert offer_order.status_code == 200

    offers = offer_order.json()
    offer_id = offers[0]["id"]

    offer_order = session.post(f'{BASE_URL}/taxi/{offer_id}/accept',
                               cookies={"my_cookie": cookie})

    order_start = session.post(f'{BASE_URL}/taxi/{order_id}/start',
                               cookies={"my_cookie": cookie}
                               )

    driver_id = order_start.json()["driver_id"]
    drivers = session.get(f'{BASE_URL}/drivers/{driver_id}',
                          cookies={"my_cookie": cookie}
                          )
    body_drivers = drivers.json()
    money_before = float(body_drivers["money"])

    assert order_start.status_code == 201

    order_finish = session.post(f'{BASE_URL}/taxi/{order_id}/finish',
                                cookies={"my_cookie": cookie}
                                )

    assert order_finish.status_code == 201

    balance = session.get(f'{BASE_URL}/pay/balance',
                          cookies={"my_cookie": cookie}
                          )
    body_balance = balance.json()
    assert balance.status_code == 200
    assert float(body_balance["balance"]) == 650.00

    driver_id = order_finish.json()["driver_id"]

    drivers = session.get(f'{BASE_URL}/drivers/{driver_id}',
                          cookies={"my_cookie": cookie}
                          )
    body_drivers = drivers.json()
    assert drivers.status_code == 200

    money_after = float(body_drivers["money"])
    expected_money = money_before + 350.0
    assert money_after == expected_money
