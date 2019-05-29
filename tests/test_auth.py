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


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        """The test client can be used in a ``with`` block to defer the closing down(延迟清理)
        of the context until the end of the ``with`` block. """
        client.get('/')
        assert session['user_id'] == 1  # 因为前面的auth.login()，因此这里才能成功
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
