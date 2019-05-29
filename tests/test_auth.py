import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    assert 'http://localhost/auth/login' == response.headers['Location']
    with app.app_context():
        assert get_db().execute(
            "select * from user where username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('', '', b'Username is required.'),
        ('a', '', b'Password is required.'),
        ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('a', 'test', 'Incorrect username.'),
        ('test', 'a', 'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.get_data(as_text=True)


def test_login(client, auth):
    assert auth._client is client  # autu._client is client, 相当于同一个客户端访问服务端, 因此session在同一个会话的多个请求间可以使用
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'
    with client:
        """The test client can be used in a ``with`` block to defer the closing down(延迟清理)
        of the context until the end of the ``with`` block. """
        client.get('/')
        assert session['user_id'] == 1  # 因为前面的auth.login()，因此这里才能成功, 而且因为autu._client正是这里的client，session才保留
        assert g.user['username'] == 'test'
        a = g.db
        x = g.user
        # 在做下一个请求前的时候，会把前一个请求的tear down钩子(flaskr.db.close_db)执行; 如果没有后一个请求，则直到跳出with才执行tear down
        # 此外，每个请求的g是独立的，在下一个请求的g的内容和上一个请求的g的内容完全没有关系
        # 当然一个请求中，可能会经历多个函数，这些函数里g内容是共享的（比如钩子函数和view函数之间g共享）
        client.get('/')
        b = g.db
        y = g.user
        assert a != b
        assert x is not y


def test_logout(client, auth):
    auth.login()
    with client:
        client.get('/')
        assert 'user_id' in session
        assert g.user is not None

        auth.logout()
        assert 'user_id' not in session
        assert g.user is not None  # logout结束后, 代码逻辑可知g.user并没有被清空

        client.get('/')
        assert 'user_id' not in session
        assert g.user is None  # 下次再登陆, 由于session不存在了, 在load_logged_in_user方法中g.user被赋值为None()
