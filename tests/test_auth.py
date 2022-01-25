import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200

    register_post_response = client.post(
        '/auth/register',
        data={'username': 'a', 'passwd': 'a'}
    )

    # If user was registered, response will redirect the client
    assert 'http://localhost/auth/login' == register_post_response.headers['Location']

    with app.app_context():
        assert get_db().execute(
            "SELECT *  FROM users WHERE username = 'a'"
        ).fetchone() is not None


# mark.parametrized tells to pytest to the function with different
# parameters
@pytest.mark.parametrize(('username', 'password', 'message'),(
    ('', '', b'Username is required'),
    ('a', '', b'Password is required'),
    ('test', 'test', b'already registered')
))
def test_register_validation_input(client, username, password, message):
    """Tests the validation of user register view by """
    register_post_response = client.post(
        '/auth/register',
        data={'username': username, 'passwd': password}
    )

    assert message in register_post_response.data


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200

    login_response = auth.login()
    assert login_response.headers['Location'] == 'http://localhost/'

    # Using client in a with block
    # allows access to context variables after the
    # request has finished
    with client:
        client.get('/')

        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'),(
        ('a', 'test', b'Incorrect username'),
        ('test', 'a', b'Incorrect password')
))
def test_login_input_validation(auth, username, password, message):
    login_response = auth.login(username, password)
    assert message in login_response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
