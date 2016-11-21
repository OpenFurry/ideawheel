import flask
import ideawheel
import os
import tempfile
import unittest


class IdeawheelTests(unittest.TestCase):

    def setUp(self):
        self.db_fd, ideawheel.app.config['DATABASE'] = tempfile.mkstemp()
        ideawheel.app.config['TESTING'] = True
        self.app = ideawheel.app.test_client()
        ideawheel.init_db()
        ideawheel.app.secret_key = os.urandom(12)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(ideawheel.app.config['DATABASE'])

    def create_user(self, username='TestUser', password='TestPassword',
                    email='TestEmail@example.com'):
        return self.app.post('/register',
                             data=dict(
                                 username=username,
                                 password=password,
                                 password2=password,
                                 email=email,
                                 hp=''
                             ), follow_redirects=True)

    def make_admin(self, username):
        with ideawheel.app.test_request_context('/'):
            ideawheel.app.preprocess_request()
            flask.g.db.execute('update auth_users set user_type=2 where '
                               'username=?', [username])
            flask.g.db.commit()

    def make_staff(self, username):
        with ideawheel.app.test_request_context('/'):
            ideawheel.app.preprocess_request()
            flask.g.db.execute('update auth_users set user_type=1 where '
                               'username=?', [username])
            flask.g.db.commit()

    def login(self, username='TestUser', password='TestPassword'):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def create_stub(self, stub_text, link=None):
        with ideawheel.app.test_request_context('/'):
            ideawheel.app.preprocess_request()
            flask.g.db.execute('insert into idea_stubs (stub, link) values '
                               '(?, ?)', [stub_text, link])
            flask.g.db.commit()


class UserManagementTestCase(IdeawheelTests):

    def test_register(self):
        # Mismatched passwords
        result = self.app.post('/register', data=dict(
            username='Test',
            password='TestPassword',
            password2='No Match',
            email='TestEmail@example.com',
            hp=''
        ), follow_redirects=True)
        self.assertIn(b'All fields are required', result.data)

        # Missing field
        result = self.app.post('/register', data=dict(
            username='Test',
            password='TestPassword',
            password2='TestPassword',
            email='',
            hp=''
        ), follow_redirects=True)
        self.assertIn(b'All fields are required', result.data)

        # Honeypot with data
        result = self.app.post('/register', data=dict(
            username='Test',
            password='TestPassword',
            password2='TestPassword',
            email='TestEmail@example.com',
            hp='Actually a spammer'
        ), follow_redirects=True)
        self.assertIn(b'All fields are required', result.data)

        # Success
        result = self.create_user()
        self.assertIn(b'Logged in as <a href="/user/TestUser">TestUser</a>',
                      result.data)

        # Duplicate user
        result = self.create_user()
        self.assertIn(b'That username or email is already in use', result.data)

    def test_login(self):
        self.create_user()

        # Success
        result = self.login()
        self.assertIn(b'Logout', result.data)

        # Bad user/pass
        result = self.login('Bad', 'User')
        self.assertIn(b'Incorrect username or password', result.data)

    def test_logout(self):
        self.create_user()
        self.login()

        # Success
        result = self.logout()
        self.assertIn(b'Login', result.data)

    def test_edit_and_view_profile(self):
        self.create_user()

        # Default data
        self.login()
        result = self.app.get('/user/TestUser')
        expected = [
            b'~TestUser',
            b'thinker of grand ideas',
            b'user',
            b'No information provided'
        ]
        for e in expected:
            self.assertIn(e, result.data)

        # New data
        result = self.app.post('/user/TestUser/edit', data=dict(
            display_name='New name',
            blurb='New blurb',
            artist_type='New artist type',
            email='NewEmail@example.com',
            password='TestPassword',
            new_password='',
            new_password2=''
        ), follow_redirects=True)
        expected = [
            b'New name',
            b'New artist type',
            b'user',
            b'New blurb'
        ]
        for e in expected:
            self.assertIn(e, result.data)
        self.logout()

        # Admin editing
        self.create_user(username='Admin', password='Admin',
                         email='Admin@example.com')
        self.make_admin('Admin')
        self.login('Admin', 'Admin')
        result = self.app.post('/user/TestUser/edit', data=dict(
            display_name='New name',
            blurb='Edited by admin',
            artist_type='New artist type',
            email='NewEmail@example.com',
            password='TestPassword',
            new_password='',
            new_password2=''
        ), follow_redirects=True)
        self.assertIn(b'Edited by admin', result.data)
        self.logout()

        # Permission denied editing someone else's profile
        self.login()
        result = self.app.post('/user/Admin/edit', data=dict(
            display_name='New name',
            blurb='Edited by non-admin',
            artist_type='New artist type',
            email='NewEmail@example.com',
            password='TestPassword',
            new_password='',
            new_password2=''
        ), follow_redirects=True)
        self.assertEqual(result.status_code, 403)
        result = self.app.get('/user/Admin')
        self.assertNotIn(b'Edited by non-admin', result.data)
        self.logout()

        # Permission denied when logged out
        result = self.app.get('/user/TestUser/edit')
        self.assertEqual(result.status_code, 403)


class IdeaStubTestCase(IdeawheelTests):

    def test_create_stub(self):
        # Staff only action - hit /stubs/create to make a new one
        # Normal user bounced
        self.login()
        result = self.app.post('/stub/create', data=dict(
            text='Sample stub text',
            title='Sample stub'
        ), follow_redirects=True)
        self.assertEqual(result.status_code, 403)

        # TODO pull into helper
        self.create_user(username='Admin', password='Admin',
                         email='Admin@example.com')
        self.make_admin('Admin')
        self.login('Admin', 'Admin')

        result = self.app.post('/stub/create', data=dict(
            stub_text='Sample stub text',
        ), follow_redirects=True)
        self.assertIn(b'Stub created', result.data)

        self.create_user(username='Staff', password='Staff',
                         email='Admin@example.com')
        self.make_staff('Staff')
        self.login('Staff', 'Staff')

        result = self.app.post('/stub/create', data=dict(
            stub_text='Sample stub text',
        ), follow_redirects=True)
        self.assertIn(b'Stub created', result.data)

    def test_random_stub(self):
        # This assumes that the randomness of SQLite works, focusing instead on
        # displaying the random stub.
        self.login()
        self.create_stub('A stub without a link')
        result = self.app.get('/idea')
        self.assertIn(b'A stub without a link', result.data)

    def test_random_stub_with_link(self):
        self.login()
        self.create_stub('A stub with a link', link='the link itself')
        result = self.app.get('/idea')
        self.assertIn(b'A stub with a link', result.data)
        self.assertIn(b'the link itself', result.data)


if __name__ == '__main__':
    unittest.main()
