from flask import (
    Blueprint,  redirect, request, render_template,
    flash, g, url_for
)


from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    db = get_db()

    posts = db.execute(
        'SELECT p.id, title, content, created, author_id, username '
        'FROM posts p JOIN users u ON u.id = author_id '
        'ORDER BY created DESC'
    ).fetchall()

    return render_template('blog/index.html', posts=posts)


@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():

    if request.method == 'POST':

        db = get_db()

        title = request.form['title']
        content = request.form['content']
        author_id = g.user['id']
        error = None
        if not title:
            error = 'Title is required'

        elif not content:
            error = 'Content is required'

        if error is not None:
            flash(error)
        else:
            db.execute(
                'INSERT INTO posts (title, content, author_id) '
                'VALUES (?, ?, ?)',
                (title, content, author_id)
            )

            db.commit()

            return redirect(url_for('blog.index'))
    return render_template('blog/create_post.html')


def get_post_by_id(post_id, check_author=True):
    db = get_db()

    post = db.execute(
        'SELECT p.id, title, content, created, author_id '
        'FROM posts p JOIN users u on u.id = author_id '
        'WHERE p.id = ?',
        (post_id,)
    ).fetchone()

    if post is None:
        abort(404, f'Post {post_id} does not exist.')

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@blog_bp.route('/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = get_post_by_id(post_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        error = None
        if not title:
            error = 'Title is required'
        elif not content:
            error = 'Content required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE posts '
                'SET title = ?, '
                'content = ? '
                'WHERE id = ?',
                (title, content, post_id)
            )

            db.commit()

            return redirect(url_for('blog.index'))

    return render_template('blog/update_post.html', post=post)


@blog_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = get_post_by_id(post_id)
    db = get_db()
    db.execute(
        'DELETE FROM posts WHERE id=?',
        (post_id,)
    )
    db.commit()

    return redirect(url_for('blog.index'))
