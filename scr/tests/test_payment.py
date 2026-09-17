from .constants import BASE_URL, USER
import pytest
import requests


@pytest.mark.smoke
@pytest.mark.parametrize("money", [
            200.0, 12.3
        ])
def test_top_up_your_card(money, test_user):
    request_data = {
        'money': money
    }
    user_id = test_user

    with requests.Session() as session:
        login_response = session.post(f'{BASE_URL}/auth/login', json=USER)
        assert login_response.status_code == 200
        cookie = session.cookies.get("my_cookie")

        result = session.post(f'{BASE_URL}/pay/top-up',
                              json=request_data,
                              cookies={"my_cookie": cookie})
        assert result.status_code == 200
