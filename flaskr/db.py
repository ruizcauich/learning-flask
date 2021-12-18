import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():

    # g is an special object used to store shared data
    # between multiple functions, it is unique for each request

    # current_app points to the Flask application handling the request
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        # Tells the conection to use dict like
        # objects as rows
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    # Open file relative to the flaskr package
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf-8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Takes and app object to register  close_db function
    and init_db_command function as command
    to be used by the application.
    
    Since the application is created using a factory function
    it is not directly available, therfore a function that
    takes an app as argument is needed. This function must be
    called from the factory function.
    """
    
    # Ensures cloes_db is called after returning the response
    app.teardown_appcontext(close_db)
    # Register the command
    app.cli.add_command(init_db_command)