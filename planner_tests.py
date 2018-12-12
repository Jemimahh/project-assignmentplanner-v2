import os
import app as planner
import unittest
import tempfile
from flask import Flask, request

# source: http://flask.pocoo.org/docs/0.12/testing/

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, planner.app.config['DATABASE'] = tempfile.mkstemp()
        planner.app.testing = True
        self.app = planner.app.test_client()
        with planner.app.app_context():
            planner.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(planner.app.config['DATABASE'])

    def create(self, username, password1, password2):
        return self.app.post('/create_account', data=dict(username=username, password=password1, password2=password2)
            ,follow_redirects=True)

    def test_create(self):
        rv = self.create("user", "pw", "pw");
        assert b"Account creation successful." in rv.data

        rv = self.create("user", "pw", "pw");
        assert b"The username already exists. Try with another username" in rv.data

        rv = self.create("new_user", "pw", "pw_does_not_match")
        assert b"Passwords do not match. Try again." in rv.data

    def login(self, username, password):
        return self.app.post('/login_account', data=dict(username=username, password=password), follow_redirects=True)

    def test_login(self):
        self.create("user", "pw", "pw")
        rv = self.login("user", "pw")
        assert b"Logged into user" in rv.data

        rv = self.login("user_dne", "pw")
        assert b"Username does not exist" in rv.data

        rv = self.login("user", "wrong_pw")
        assert b"Wrong username and password. Try again" in rv.data

    def test_logout(self):
        self.create("user", "pw", "pw")
        rv = self.login("user", "pw")
        rv = self.app.get('/logout', follow_redirects=True)
        assert b"You were logged out" in rv.data

    def test_empty_db(self):
        self.create("user", "pw", "pw")
        self.login("user", "pw")
        rv = self.app.get('/assignments')
        assert b"You don't have any assignments currently." in rv.data


    # modified login() code from the following source
    # http://flask.pocoo.org/docs/0.12/testing/
    def add_entry(self, title, course, category, priority, duedate, description):
        return self.app.post('/add',
            data=dict(title=title, course=course, category=category, priority=priority,
                      duedate=duedate, description=description), follow_redirects=True)

    def test_add_entry(self):
        rv = self.add_entry('title1', 'CS253', 'None', 'High', '1111-11-11T11:11', 'D1')
        assert b"Unauthorized" in rv.data

        self.create("user", "pw", "pw")
        self.login("user", "pw")
        rv = self.add_entry('title1', 'CS253', 'None', 'High', '1111-11-11T11:11', 'D1')
        assert b"title1" in rv.data
        assert b"New assignment was successfully saved." in rv.data


    def test_show_assignment(self):
        self.create("user", "pw", "pw")
        self.login("user", "pw")

        self.add_entry('title1', 'CS253', 'None', 'High', '1111-11-11T11:11', 'D1')
        self.add_entry('title2', 'CS253', 'None', 'High', '1111-11-11T11:11', 'D2')
        rv = self.app.get('/assignments')
        assert b"title1" in rv.data
        assert b"title2" in rv.data


    def delete_entry(self, delete):
        self.create("user", "pw", "pw")
        self.login("user", "pw")
        return self.app.post('/delete', data=dict(id=delete), follow_redirects=True)

    def test_delete_entry(self):
        self.create("user", "pw", "pw")
        self.login("user", "pw")

        rv = self.add_entry('title1', 'CS253', 'None', 'High', '1111-11-11T11:11', 'D1')
        assert b"title1" in rv.data

        rv = self.add_entry('title2', 'CS253', 'None', 'High', '1111-11-11T11:11', 'D2')
        assert b"title2" in rv.data

        rv = self.add_entry('title3', 'CS253.3', 'None', 'High','1111-11-11T11:11', 'D3')
        assert b"title3" in rv.data

        # delete second post
        rv = self.delete_entry(2)
        assert b"title2" not in rv.data


        # then, delete the top post (with id=3)
        rv = self.delete_entry(3)
        assert b"title3" not in rv.data
        assert b"title1" in rv.data

        # then, delete the remaining post (with id=1)
        rv = self.delete_entry(1)
        assert b"title1" not in rv.data

    def edit_entry(self, title, course, category, priority, duedate, description, id):
        self.create("user", "pw", "pw")
        self.login("user", "pw")
        return self.app.post('/edit_assignment',
            data=dict(title=title, course=course, category=category, priority=priority,
                      duedate=duedate, description=description, id=id), follow_redirects=True)

    def test_edit_entry(self):
        self.create("user", "pw", "pw")
        self.login("user", "pw")

        rv = self.add_entry('title1', 'CS253.1', 'None', 'High', '1111-11-11T11:11', 'D1')
        assert b"title1" in rv.data

        # test case for when title is edited as empty
        rv = self.edit_entry('title1-edit', 'CS253.1-edit', 'None-edit', 'Low', '2222-22-22T22:22', 'D1-edit', 1)
        assert b"title1-edit" in rv.data
        assert b"CS253.1-edit" in rv.data
        assert b"None-edit" in rv.data
        assert b"Low" in rv.data
        assert b"2222-22-22T22:22" in rv.data
        assert b"D1-edit" in rv.data

    def test_calendar(self):
        self.create("user", "pw", "pw")
        self.login("user", "pw")

        self.add_entry('title1', 'CS253', 'None', 'High', '2018-01-30', 'D1')
        self.add_entry('title2', 'CS253', 'None', 'High', '2018-02-20', 'D1')
        self.add_entry('title3', 'CS253', 'None', 'High', '2019-04-20', 'D1')

        rv = self.app.get('/showcalendar?month=1&year=2018')
        assert b"January 2018" in rv.data
        assert b"title1" in rv.data
        assert b"title2" not in rv.data
        assert b"title3" not in rv.data

        rv = self.app.get('/showcalendar?month=2&year=2018')
        assert b"February 2018" in rv.data
        assert b"title1" not in rv.data
        assert b"title2" in rv.data
        assert b"title3" not in rv.data

        rv = self.app.get('/showcalendar?month=3&year=2018')
        assert b"title1" not in rv.data
        assert b"title2" not in rv.data
        assert b"title3" not in rv.data

    def test_sort(self):
        self.create("user", "pw", "pw")
        self.login("user", "pw")

        self.add_entry('title1', 'CS253', 'C1', 'Critical', '2018-01-30', 'D1')
        self.add_entry('title2', 'CS254', 'C2', 'High', '2018-02-20', 'D2')
        self.add_entry('title3', 'CS255', 'C3', 'Normal', '2019-03-20', 'D3')
        self.add_entry('title4', 'CS256', 'C4', 'Low', '2018-04-30', 'D4')


        rv = self.app.get('/assignments?arrange=title')
        assert b"<tr class=critical>"
        b"<td>title1</td><td>CS253</td><td>C1</td><td>Critical</td><td>2018-01-30</td><td>D1</td></tr>"
        b"<tr class=high><td>title2</td><td>CS254</td><td>C2</td><td>High</td><td>2018-02-20</td><td>D2</td>"
        b"</tr>"
        b"<tr class=normal>"
        b"<td>title3</td><td>CS255</td><td>C3</td><td>Normal</td><td>2018-03-20</td><td>D3</td>"
        b"</tr>"
        b"<tr class=low><td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>" in rv.data

        rv = self.app.get('/assignments?sort=title')
        assert b"<tr class=low>"
        b"<td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>"
        b"<tr class=low><td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>"
        b"<tr class=normal>"
        b"<td>title3</td><td>CS255</td><td>C3</td><td>Normal</td><td>2018-03-20</td><td>D3</td>"
        b"</tr>"
        b"<tr class=high><td>title2</td><td>CS254</td><td>C2</td><td>High</td><td>2018-02-20</td><td>D2</td>"
        b"</tr>"
        b"<tr class=critical>"
        b"<td>title1</td><td>CS253</td><td>C1</td><td>Critical</td><td>2018-01-30</td><td>D1</td></tr>" in rv.data


        rv = self.app.get('/assignments?arrange=course')
        assert b"<tr class=critical>"
        b"<td>title1</td><td>CS253</td><td>C1</td><td>Critical</td><td>2018-01-30</td><td>D1</td></tr>"
        b"<tr class=high><td>title2</td><td>CS254</td><td>C2</td><td>High</td><td>2018-02-20</td><td>D2</td>"
        b"</tr>"
        b"<tr class=normal>"
        b"<td>title3</td><td>CS255</td><td>C3</td><td>Normal</td><td>2018-03-20</td><td>D3</td>"
        b"</tr>"
        b"<tr class=low><td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>" in rv.data

        rv = self.app.get('/assignments?sort=course')
        assert b"<tr class=low>"
        b"<td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>"
        b"<tr class=low><td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>"
        b"<tr class=normal>"
        b"<td>title3</td><td>CS255</td><td>C3</td><td>Normal</td><td>2018-03-20</td><td>D3</td>"
        b"</tr>"
        b"<tr class=high><td>title2</td><td>CS254</td><td>C2</td><td>High</td><td>2018-02-20</td><td>D2</td>"
        b"</tr>"
        b"<tr class=critical>"
        b"<td>title1</td><td>CS253</td><td>C1</td><td>Critical</td><td>2018-01-30</td><td>D1</td></tr>" in rv.data

        rv = self.app.get('/assignments?arrange=category')
        assert b"<tr class=critical>"
        b"<td>title1</td><td>CS253</td><td>C1</td><td>Critical</td><td>2018-01-30</td><td>D1</td></tr>"
        b"<tr class=high><td>title2</td><td>CS254</td><td>C2</td><td>High</td><td>2018-02-20</td><td>D2</td>"
        b"</tr>"
        b"<tr class=normal>"
        b"<td>title3</td><td>CS255</td><td>C3</td><td>Normal</td><td>2018-03-20</td><td>D3</td>"
        b"</tr>"
        b"<tr class=low><td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>" in rv.data

        rv = self.app.get('/assignments?sort=category')
        assert b"<tr class=low>"
        b"<td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>"
        b"<tr class=low><td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>"
        b"<tr class=normal>"
        b"<td>title3</td><td>CS255</td><td>C3</td><td>Normal</td><td>2018-03-20</td><td>D3</td>"
        b"</tr>"
        b"<tr class=high><td>title2</td><td>CS254</td><td>C2</td><td>High</td><td>2018-02-20</td><td>D2</td>"
        b"</tr>"
        b"<tr class=critical>"
        b"<td>title1</td><td>CS253</td><td>C1</td><td>Critical</td><td>2018-01-30</td><td>D1</td></tr>" in rv.data

        rv = self.app.get('/assignments?arrange=priority')
        assert b"<tr class=critical>"
        b"<td>title1</td><td>CS253</td><td>C1</td><td>Critical</td><td>2018-01-30</td><td>D1</td></tr>"
        b"<tr class=high><td>title2</td><td>CS254</td><td>C2</td><td>High</td><td>2018-02-20</td><td>D2</td>"
        b"</tr>"
        b"<tr class=normal>"
        b"<td>title3</td><td>CS255</td><td>C3</td><td>Normal</td><td>2018-03-20</td><td>D3</td>"
        b"</tr>"
        b"<tr class=low><td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>" in rv.data

        rv = self.app.get('/assignments?sort=priority')
        assert b"<tr class=low>"
        b"<td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>"
        b"<tr class=low><td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>"
        b"<tr class=normal>"
        b"<td>title3</td><td>CS255</td><td>C3</td><td>Normal</td><td>2018-03-20</td><td>D3</td>"
        b"</tr>"
        b"<tr class=high><td>title2</td><td>CS254</td><td>C2</td><td>High</td><td>2018-02-20</td><td>D2</td>"
        b"</tr>"
        b"<tr class=critical>"
        b"<td>title1</td><td>CS253</td><td>C1</td><td>Critical</td><td>2018-01-30</td><td>D1</td></tr>" in rv.data

        rv = self.app.get('/assignments?arrange=duedate')
        assert b"<tr class=critical>"
        b"<td>title1</td><td>CS253</td><td>C1</td><td>Critial</td><td>2018-01-30</td><td>D1</td></tr>"
        b"<tr class=high><td>title2</td><td>CS254</td><td>C2</td><td>High</td><td>2018-02-20</td><td>D2</td>"
        b"</tr>"
        b"<tr class=normal>"
        b"<td>title3</td><td>CS255</td><td>C3</td><td>Normal</td><td>2018-03-20</td><td>D3</td>"
        b"</tr>"
        b"<tr class=low><td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>" in rv.data

        rv = self.app.get('/assignments?sort=duedate')
        assert b"<tr class=low>"
        b"<td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>"
        b"<tr class=low><td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>"
        b"<tr class=normal>"
        b"<td>title3</td><td>CS255</td><td>C3</td><td>Normal</td><td>2018-03-20</td><td>D3</td>"
        b"</tr>"
        b"<tr class=high><td>title2</td><td>CS254</td><td>C2</td><td>High</td><td>2018-02-20</td><td>D2</td>"
        b"</tr>"
        b"<tr class=critical>"
        b"<td>title1</td><td>CS253</td><td>C1</td><td>Critical</td><td>2018-01-30</td><td>D1</td></tr>" in rv.data

        rv = self.app.get('/assignments?arrange=description')
        assert b"<tr class=critical>"
        b"<td>title1</td><td>CS253</td><td>C1</td><td>Critical</td><td>2018-01-30</td><td>D1</td></tr>"
        b"<tr class=high><td>title2</td><td>CS254</td><td>C2</td><td>High</td><td>2018-02-20</td><td>D2</td>"
        b"</tr>"
        b"<tr class=normal>"
        b"<td>title3</td><td>CS255</td><td>C3</td><td>Normal</td><td>2018-03-20</td><td>D3</td>"
        b"</tr>"
        b"<tr class=low><td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>" in rv.data

        rv = self.app.get('/assignments?sort=description')
        assert b"<tr class=low>"
        b"<td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>"
        b"<tr class=low><td>title4</td><td>CS256</td><td>C4</td><td>Low</td><td>2018-04-20</td><td>D4</td>"
        b"</tr>"
        b"<tr class=normal>"
        b"<td>title3</td><td>CS255</td><td>C3</td><td>Normal</td><td>2018-03-20</td><td>D3</td>"
        b"</tr>"
        b"<tr class=high><td>title2</td><td>CS254</td><td>C2</td><td>High</td><td>2018-02-20</td><td>D2</td>"
        b"</tr>"
        b"<tr class=critical>"
        b"<td>title1</td><td>CS253</td><td>C1</td><td>Critical</td><td>2018-01-30</td><td>D1</td></tr>" in rv.data


if __name__ == '__main__':
    unittest.main()
