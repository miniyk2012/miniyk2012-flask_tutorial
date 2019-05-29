from click.testing import Result

from flaskr.db import get_db
import sqlite3
import pytest


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db == get_db()
        db.execute('SELECT 1')
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    assert 'closed' in str(e)


def test_init_db_command(runner, monkeypatch):
    """monkeypatch是pytest自带的fixture"""
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)  # 类似于mockito
    result: Result = runner.invoke(args=['init-db'])
    assert Recorder.called
    assert 'Initialized the database.' in result.output

