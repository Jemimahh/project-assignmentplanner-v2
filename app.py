"""
    Assignment Planner
    ~~~~~~
    This code is based off of a microblog example application written as Flask tutorial with
    Flask and sqlite3.
    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os, calendar
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

# create our little application :)
app = Flask(__name__)


# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'planner.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

logged_in_account = ""

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


@app.route('/assignments')
def show_assignment():
    db = get_db()

    if "duedate" in request.args:
        cur = db.execute('select * from assignments where username = ? and duedate = ? order by id desc',
                         [logged_in_account, request.args["duedate"]])
        assignments = cur.fetchall()

    elif "arrange" in request.args:
        cur = db.execute(
                         'select * from assignments where username = ? order by {} ASC'.format(request.args["arrange"],
                                                                            [logged_in_account])
        )
        assignments = cur.fetchall()

    elif "sort" in request.args:
        cur = db.execute('select * from assignments where username = ? order by {} DESC'.format(request.args["sort"],
                                                                            [logged_in_account])

        )

        assignments = cur.fetchall()

    else:

        cur = db.execute('select * from assignments where username = ? order by id desc', [logged_in_account])
        assignments = cur.fetchall()
    cur = db.execute('select distinct duedate from assignments order by duedate asc')


    duedates = cur.fetchall()
    return render_template('show_assignments.html', assignments=assignments, duedates=duedates)


@app.route('/add')
def redirect_add_assignment():
    return render_template('MainPageLayout.html')


@app.route('/')
def redirect_opening():
    return render_template('OpeningPage.html')

@app.route('/login')
def redirect_login():
    return render_template('Login.html')


@app.route('/signup')
def redirect_signup():
    return render_template('CreateAccount.html')


@app.route('/add', methods=['POST'])
def add_assignment():
    if not session.get(logged_in_account):
        abort(401)

    db = get_db()
    db.execute('insert into assignments (username, title, course, category, duedate, description) values (?, ?, ?, ?, ?, ?)',
               [logged_in_account, request.form['title'], request.form['course'], request.form['category'],
                request.form['duedate'], request.form['description']])
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


@app.route('/edit', methods=['GET'])
def edit_entry():
    db = get_db()
    cur = db.execute('select * from assignments where id=?', request.args['editid'])
    assignments = cur.fetchall()
    return render_template('edit_layout.html', assignments=assignments)


@app.route('/edit_assignment', methods=['POST'])
def update_entry():
    db = get_db()
    theid = request.form['id']
    title = request.form['title']
    course = request.form['course']
    category = request.form['category']
    duedate = request.form['duedate']
    description = request.form['description']
    db.execute('update assignments set title = ?, course = ?, category = ?, duedate = ?, description = ? where id = ?',
               (title, course, category, duedate, description, theid))
    db.commit()
    # Commits it to the database
    flash('New entry was successfully edited')
    return show_assignment()


@app.route('/assignments', methods=['POST'])
def create_account():
    db = get_db()
    validate = db.execute('select username from accounts where username=?', [request.form['username']])
    data = db.execute('select * from accounts')

    if validate.fetchall():
        flash('The username already exists. Try with another username')
        for record in data:
            print(dict(record))
        return redirect(url_for('redirect_signup'))
    else:
        password = request.form['password']
        re_password = request.form['password2']

        if password != re_password:
            flash('Passwords do not match. Try again.')
            for record in data:
                print(dict(record))
            return redirect(url_for('redirect_signup'))
        else:

            db.execute('insert into accounts (username, password) values (?, ?)',
                    [request.form['username'], password])
            db.commit()
        flash('Account creation successful.')

    for record in data:
        print(dict(record))
    return redirect(url_for('redirect_login'))


@app.route('/login_account', methods=['POST'])
def login_account():
    db = get_db()
    username = request.form['username']
    validate_account = db.execute('select username, password from accounts where username=?', [username])
    data = validate_account
    data = dict(data)

    if db.execute('select username, password from accounts where username=?', [username]).fetchall():
        password = request.form['password']

        if data.get(username) == password:
            global logged_in_account
            session[username] = True
            session['logged_in'] = True
            logged_in_account = username
            flash('Logged into ' + username)
            return redirect(url_for('show_assignment'))

        else:
            flash('Wrong username and password. Try again')

    else:
        flash('Username does not exist')
    return redirect(url_for('redirect_login'))


@app.route('/logout')
def logout():
    global logged_in_account
    session.pop('logged_in', None)
    session.pop(logged_in_account, None)
    flash('You were logged out')
    logged_in_account = ""
    return redirect(url_for('redirect_login'))


@app.route('/homepage')
def display_homepage():
    return render_template('home.html', username = logged_in_account)


# @app.route('/calendar')
# def display_calendar():
#     db = get_db()
#
#     if "duedate" in request.args:
#         cur = db.execute('select * from assignments where username = ? and duedate = ? order by id desc',
#                          [logged_in_account, request.args["duedate"]])
#         assignments = cur.fetchall()
#
#     elif "arrange" in request.args:
#         cur = db.execute(
#                          'select * from assignments where username = ? order by {} ASC'.format(request.args["arrange"],
#                                                                             [logged_in_account])
#         )
#         assignments = cur.fetchall()
#
#     elif "sort" in request.args:
#         cur = db.execute('select * from assignments where username = ? order by {} DESC'.format(request.args["sort"],
#                                                                             [logged_in_account])
#         )
#
#         assignments = cur.fetchall()
#
#     else:
#
#         cur = db.execute('select * from assignments where username = ? order by id desc', [logged_in_account])
#         assignments = cur.fetchall()
#     cur = db.execute('select distinct duedate from assignments order by duedate asc')
#
#     duedates = cur.fetchall()
#
#     mo = 12 # mo = request.args[month]
#     yr = 2018 # yr = request.args[year]
#     print(calendar.month(yr,mo))
#     print("display")
#     return render_template('Calendar.html', username = logged_in_account, assignments=assignments, duedates=duedates)

@app.route('/calendar')
def display_calendar():
    return render_template('Calendar.html')

@app.route('/showcalendar', methods=['GET'])
def input_calendar():
    mo = int(request.args['month'])
    yr = int(request.args['year'])
    myCal = calendar.HTMLCalendar(calendar.SUNDAY)
    newCal = myCal.formatmonth(yr, mo)
    print (newCal)
    print("hello")
    return render_template('Calendar.html', calendar = newCal, username = logged_in_account)