import os
import app as planner
import unittest
import tempfile

class PlannerTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, planner.app.config['DATABASE'] = tempfile.mkstemp()
        planner.app.testing = True
        self.app = planner.app.test_client()
        with planner.app.app_context():
            planner.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(planner.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    # Test the messages below
    def test_add_entry(self):
        # defining variables in our new database
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            classes='<Hello>',
            category='<CATegory>',
            description='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        # Check for expected result
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'&lt;CATegory&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

    def test_show_entry(self):
        # add a post
        self.app.post('/add', data=dict(
            title='<Hello>',
            classes='<Hello>',
            category='<CATegory>',
            description='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        # get the show entries page
        rv = self.app.get('/')
        # check for result
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'&lt;CATegory&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data

    def test_delete_entry(self):
        # add a post
        self.app.post('/add', data=dict(
            id = '1',
            title='<Hello>',
            classes='<Hello>',
            category='<CATegory>',
            description='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        # delete post with matching id
        rv = self.app.post('/delete', data=dict(
            deletethispost = '1'
        ), follow_redirects=True)
        assert b'&lt;Hello&gt;' not in rv.data
        assert b'&lt;CATegory&gt;' not in rv.data
        assert b'<strong>HTML</strong> allowed here' not in rv.data
        assert b'No entries here so far' in rv.data

    def test_edit_entry(self):
        self.app.post('/add', data=dict(
            id='1',
            title='<Hello>',
            classes='<Hello>',
            category='<CATegory>',
            duedate='<Hello>',
            description='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        # delete post with matching id
        rv = self.app.post('/edit', data=dict(
            id='1',
            title='<Hello>',
            classes='<Hello>',
            category='<CATegory>',
            duedate='<Hello>',
            description='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Goodbye&gt;' in rv.data
        assert b'&lt;NewCAT&gt;' in rv.data
        assert b'<strong>HTML</strong> NOT allowed here' in rv.data