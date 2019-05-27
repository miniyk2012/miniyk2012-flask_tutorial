import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
import inspect

def get_db():
    """g is a special object that is unique for each request.
    It is used to store data that might be accessed by multiple functions during the request.
    The connection is stored and reused instead of creating a new connection
    if get_db is called a second time in the same request."""
    if 'db' not in g:
        print('get a new connect')
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    print('caller name:', inspect.stack()[1][3])
    print('get_db is called')
    return g.db


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def close_db(e=None):
    db = g.pop('db', None)
    print(f'close the db, db is {db}')
    if db is not None:
        db.close()


def init_app(app):
    # app.teardown_appcontext tells Flask to call that function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # app.cli.add_command() adds a new command that can be called with the flask command.
    app.cli.add_command(init_db_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
