import flask, ideawheel, os, tempfile, unittest

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

    def create_user(self, username = 'TestUser', password = 'TestPassword',
            email = 'TestEmail@example.com'):
        return self.app.post('/register', data = dict(
            username = username,
            password = password,
            password2 = password,
            email = email,
            hp = ''
        ), follow_redirects = True)

    def make_admin(self, username):
        with ideawheel.app.test_request_context('/'):
            ideawheel.app.preprocess_request()
            flask.g.db.execute('update auth_users set user_type = 2 where '
                    'username = ?', [username])
            flask.g.db.commit()

    def login(self, username = 'TestUser', password = 'TestPassword'):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects = True)

    def logout(self):
        return self.app.get('/logout', follow_redirects = True)

class UserManagementTestCase(IdeawheelTests):
    def test_register(self):
        # Mismatched passwords
        result = self.app.post('/register', data = dict(
            username = 'Test',
            password = 'TestPassword',
            password2 = 'No Match',
            email = 'TestEmail@example.com',
            hp = ''
        ), follow_redirects = True)
        self.assertTrue('All fields are required' in result.data)

        # Missing field
        result = self.app.post('/register', data = dict(
            username = 'Test',
            password = 'TestPassword',
            password2 = 'TestPassword',
            email = '',
            hp = ''
        ), follow_redirects = True)
        self.assertTrue('All fields are required' in result.data)

        # Honeypot with data
        result = self.app.post('/register', data = dict(
            username = 'Test',
            password = 'TestPassword',
            password2 = 'TestPassword',
            email = 'TestEmail@example.com',
            hp = 'Actually a spammer'
        ), follow_redirects = True)
        self.assertTrue('All fields are required' in result.data)

        # Success
        result = self.create_user()
        self.assertTrue('Logged in as <a href="/user/TestUser">TestUser</a>' \
                in result.data)

        # Duplicate user
        result = self.create_user()
        self.assertTrue('That username or email is already in use' in result.data)

    def test_login(self):
        self.create_user()

        # Success
        result = self.login()
        self.assertTrue('Logout' in result.data)

        # Bad user/pass
        result = self.login('Bad', 'User')
        self.assertTrue('Incorrect username or password' in result.data)

    def test_logout(self):
        self.create_user()
        self.login()

        # Success
        result = self.logout()
        self.assertTrue('Login' in result.data)

    def test_edit_and_view_profile(self):
        self.create_user()
        
        # Default data
        self.login()
        result = self.app.get('/user/TestUser')
        expected = [
                '~TestUser',
                'thinker of grand ideas',
                'user',
                'No information provided'
                ]
        for e in expected:
            self.assertTrue(e in result.data)

        # New data
        result = self.app.post('/user/TestUser/edit', data = dict(
            display_name = 'New name',
            blurb = 'New blurb',
            artist_type = 'New artist type',
            email = 'NewEmail@example.com',
            password = 'TestPassword',
            new_password = '',
            new_password2 = ''
        ), follow_redirects = True)
        expected = [
                'New name',
                'New artist type',
                'user',
                'New blurb'
                ]
        for e in expected:
            self.assertTrue(e in result.data)
        self.logout()

        # Admin editing
        self.create_user(username = 'Admin', password = 'Admin',
                email = 'Admin@example.com')
        self.make_admin('Admin')
        self.login('Admin', 'Admin')
        result = self.app.post('/user/TestUser/edit', data = dict(
            display_name = 'New name',
            blurb = 'Edited by admin',
            artist_type = 'New artist type',
            email = 'NewEmail@example.com',
            password = 'TestPassword',
            new_password = '',
            new_password2 = ''
        ), follow_redirects = True)
        self.assertTrue('Edited by admin' in result.data)
        self.logout()

        # Permission denied editing someone else's profile
        self.login()
        result = self.app.post('/user/Admin/edit', data = dict(
            display_name = 'New name',
            blurb = 'Edited by non-admin',
            artist_type = 'New artist type',
            email = 'NewEmail@example.com',
            password = 'TestPassword',
            new_password = '',
            new_password2 = ''
        ), follow_redirects = True)
        self.assertEqual(result.status_code, 403)
        result = self.app.get('/user/Admin')
        self.assertTrue('Edited by non-admin' not in result.data)
        self.logout()

        # Permission denied when logged out
        result = self.app.get('/user/TestUser/edit')
        self.assertEqual(result.status_code, 403)

class IdeaStubTestCase(IdeawheelTests):
    def test_create_stub(self):
        # Admin only action - hit /stubs/create to make a new one
        # Normal user bounced
        self.login()
        result = self.app.post('/stub/create', data = dict(
            text = 'Sample stub text',
            title = 'Sample stub'
        ), follow_redirects = True)
        self.assertEqual(result.status_code, 403)

        # TODO pull into helper
        self.create_user(username = 'Admin', password = 'Admin',
                email = 'Admin@example.com')
        self.make_admin('Admin')
        self.login('Admin', 'Admin')

        result = self.app.post('/stub/create', data = dict(
            stub_text = 'Sample stub text',
        ), follow_redirects = True)
        self.assertTrue('Stub created' in result.data)

if __name__ == '__main__':
    unittest.main()
