import pytest
from flaskr.db import get_db


def test_index_with_anonymous_user(client):
    response = client.get('/')
    assert b'Iniciar Sesi' in response.data
    assert b'Registrate' in response.data


def test_index_with_logged_in_user(client, auth):
    auth.login()
    response = client.get('/')

    assert b'Cerrar Sesi' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/auth/login'


def test_author_required(app, client, auth):

    auth.login()

    # The update link is available only for the post author
    assert b'href="/1/update"' in client.get('/').data

    # change author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE posts SET author_id=2 WHERE id = 1')
        db.commit()

    # The current user cannot update, delete, or see
    # the update link on the index page
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403


@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete'
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create_post(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'content': 'new post'})

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM posts').fetchone()[0]
        assert count == 2


def test_update_post(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200

    client.post('/1/update', data={'title': 'updated', 'content': 'updated'})

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM posts WHERE id=1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update'
))
def test_create_update_validation(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'content': ''})
    assert b'Title is required' in response.data


def test_delete(client, app, auth):
    auth.login()
    response = client.post('/1/delete')

    assert response.headers['Location'] == 'http://localhost/'

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM posts WHERE id=1').fetchone()
        assert post is None
