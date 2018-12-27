"""
    Assignment Planner
    ~~~~~~
    This code is based off of a microblog example application written as Flask tutorial with
    Flask and sqlite3.
    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
import calendar
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


@app.route('/create_account', methods=['POST'])
def create_account():
    db = get_db()
    validate = db.execute('select username from accounts where username=?', [request.form['username']])

    if validate.fetchall():
        flash('The username already exists. Try with another username')
        return redirect(url_for('redirect_signup'))
    else:
        password = request.form['password']
        re_password = request.form['password2']

        if password != re_password:
            flash('Passwords do not match. Try again.')
            return redirect(url_for('redirect_signup'))
        else:

            db.execute('insert into accounts (username, password) values (?, ?)',
                    [request.form['username'], password])
            db.commit()
        flash('Account creation successful.')

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
            session['logged_in'] = username
            flash('Logged into ' + username)
            return redirect(url_for('show_assignment'))

        else:
            flash('Wrong username and password. Try again')

    else:
        flash('Username does not exist')
    return redirect(url_for('redirect_login'))


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('redirect_login'))


@app.route('/homepage')
def display_homepage():
    # now = datetime.datetime.now()
    # today = now.strftime("%Y-%m-%d %I:%M")
    if 'logged_in' in session:
        username = session['logged_in']
        db = get_db()

        cur = db.execute('select * from assignments where username = ? order by id desc', [username])
        assignments = cur.fetchall()

        critical = db.execute("select count(*) from assignments where username = ? and priority = 'Critical'",
                         [username])
        high = db.execute("select count(*) from assignments where username = ? and priority = 'High'",
                         [username])
        normal = db.execute("select count(*) from assignments where username = ? and priority = 'Normal'",
                         [username])
        low = db.execute("select count(*) from assignments where username = ? and priority = 'Low'",
                         [username])

        priority1 = critical.fetchone()
        number_of_critical = priority1[0]
        priority2 = high.fetchone()
        number_of_high = priority2[0]
        priority3 = normal.fetchone()
        number_of_normal = priority3[0]
        priority4 = low.fetchone()
        number_of_low = priority4[0]

        return render_template('Homepage.html', username=username, critical=number_of_critical,
                               high=number_of_high, normal=number_of_normal, low=number_of_low, assignments=assignments)

    return render_template('OpeningPage.html')


@app.route('/assignments')
def show_assignment():

    if 'logged_in' in session:
        db = get_db()
        username = session['logged_in']

        if "duedate" in request.args:
            cur = db.execute('select * from assignments where username = ? and duedate = ? order by id desc',
                             [username, request.args["duedate"]])
            assignments = cur.fetchall()

        elif "arrange" in request.args:

            cur = db.execute('select * from assignments where username = ? order by {} ASC'.format(request.args["arrange"]),
                            [username])

            assignments = cur.fetchall()

        elif "sort" in request.args:
            cur = db.execute('select * from assignments where username = ? order by {} DESC'.format(request.args["sort"]),
                            [username])

            assignments = cur.fetchall()

        else:

            cur = db.execute('select * from assignments where username = ? order by id desc', [username])
            assignments = cur.fetchall()

        cur = db.execute('select distinct duedate from assignments where username = ? order by duedate asc', [username])


        duedates = cur.fetchall()
        return render_template('ShowAssignments.html', assignments=assignments, duedates=duedates)

    return render_template('Login.html')


@app.route('/delete', methods=['POST'])
def del_assignment():
    if 'logged_in' in session:
        db = get_db()
        db.execute('delete from assignments where id=?', [request.form['id']])
        db.commit()
        flash('Assignment has been deleted')
        return redirect(url_for('show_assignment'))
    return render_template('Login.html')


@app.route('/edit', methods=['GET'])
def edit_entry():
    if 'logged_in' in session:
        db = get_db()
        cur = db.execute('select * from assignments where id = ?', [request.args['editid']])
        assignments = cur.fetchall()
        return render_template('EditAssignment.html', assignments=assignments)
    return render_template('Login.html')


@app.route('/edit_assignment', methods=['POST'])
def update_entry():
    if 'logged_in' in session:
        db = get_db()
        theid = request.form['id']
        title = request.form['title']
        course = request.form['course']
        category = request.form['category']
        priority = request.form['priority']
        duedate = request.form['duedate']
        description = request.form['description']
        db.execute('update assignments set title = ?, course = ?, category = ?, priority = ?, duedate = ?, description = ?'
            'where id = ?', [title, course, category, priority, duedate, description, theid])
        db.commit()
        # Commits it to the database
        flash('New entry was successfully edited')
        return redirect(url_for('show_assignment'))
    return render_template('Login.html')


@app.route('/add', methods=['POST'])
def add_assignment():
    if not session.get('logged_in'):
        abort(401)

    db = get_db()
    db.execute('insert into assignments (username, title, course, category, priority, duedate, description) '
               'values (?, ?, ?, ?, ?, ?, ?)', [session['logged_in'], request.form['title'], request.form['course'],
                request.form['category'], request.form['priority'], request.form['duedate'], request.form['description']])
    # request.form gets request in a post request
    # Puts the values from the show_entries.html form into the database as (title, category, text)
    db.commit()
    # Commits it to the database
    flash('New assignment was successfully saved.')
    return redirect(url_for('show_assignment'))


@app.route('/add')
def redirect_add_assignment():
    if 'logged_in' in session:
        username = session['logged_in']
        return render_template('AddAssignment.html', username=username)
    return render_template('Login.html')


@app.route('/')
def redirect_opening():
    if 'logged_in' in session:
        return redirect(url_for('display_homepage'))
    return render_template('OpeningPage.html')


@app.route('/login')
def redirect_login():
    if 'logged_in' in session:
        return redirect(url_for('display_homepage'))
    return render_template('Login.html')


@app.route('/signup')
def redirect_signup():
    if 'logged_in' in session:
        return redirect(url_for('display_homepage'))
    return render_template('CreateAccount.html')


@app.route('/full_view', methods=['GET'])
def full_view():
    if 'logged_in' in session:
        db = get_db()
        cur = db.execute('select * from assignments where id = ?', [request.args['id']])
        assignments = cur.fetchall()
        return render_template('full_view.html', assignments=assignments)
    return render_template('Login.html')


@app.route('/calendar')
def display_calendar():
    if 'logged_in' in session:
        return render_template('Calendar.html')
    return render_template('Login.html')


@app.route('/showcalendar', methods=['GET'])
def input_calendar():
    if 'logged_in' in session:
        db = get_db()

        month = request.args['month']
        year = request.args['year']

        if len(month) == 1:
            # for cases like when user enters "1" for January, instead of "01"
            month = "0" + month

        like_str = "{}-{}-%".format(year, month)

        cur = db.execute("select * from assignments where username = ? and duedate like ? order by duedate ASC",
                         [session['logged_in'], like_str])

        assignments = cur.fetchall()

        if month == "":
            flash("Month cannot be empty.")

        else:
            if (int(month) < 1) or (int(month) > 12):
                flash("Month should be between 1 and 12 inclusively.")

        if year == "":
            flash("Year cannot be empty.")

        if month != "" and year != "":
            mo = int(request.args['month'])
            yr = int(request.args['year'])
            myCal = calendar.HTMLCalendar(calendar.SUNDAY)
            newCal = myCal.formatmonth(yr, mo)

            return render_template('Calendar.html', calendar=newCal, assignments=assignments)

        return redirect(url_for('display_calendar'))

    return render_template('Login.html')