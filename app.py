"""
    Assignment Planner
    ~~~~~~

    This code is based off of a microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash
# create our little application :)
app = Flask(__name__)


# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'planner.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()



@app.route('/')
def show_assignment():
    db = get_db()

    if "duedate" in request.args:
        cur = db.execute('select id, title, class, duedate, description from assignments where duedate = ? order by id desc',
                         [request.args["duedate"]])
        assignments = cur.fetchall()
    else:
        cur = db.execute('select id, title, class, duedate, description from assignments order by id desc')
        assignments = cur.fetchall()

    cur = db.execute('select distinct duedate from assignments order by duedate asc')
    duedates = cur.fetchall()
    return render_template('show_assignments.html', assignments=assignments, duedates=duedates)

@app.route('/main')
def redirect_mainpage():
    db = get_db()
    cur = db.execute('select * from assignments order by id desc')
    assignments = cur.fetchall()
    return render_template('MainPageLayout.html', assignments=assignments)

@app.route('/add', methods=['POST'])
def add_assignment():
    db = get_db()
    db.execute('insert into assignments (title, class, category, duedate, description) values (?, ?, ?, ?,?)',
               [request.form['title'], request.form['class'],request.form['category'], request.form['duedate'], request.form['description']])
    # request.form gets request in a post request
    # Puts the values from the show_entries.html form into the database as (title, category, text)
    db.commit()
    # Commits it to the database
    flash('New assignment was successfully saved.')
    return redirect(url_for('show_assignment'))


@app.route('/delete', methods=['POST'])
def del_assignment():
    db = get_db()
    db.execute('delete from assignments where id=?', [request.form['id']])
    db.commit()
    flash('Assignment has been deleted')
    return redirect(url_for('show_assignment'))