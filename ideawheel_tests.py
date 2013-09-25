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

    def create_user(self):
        return self.app.post('/register', data = dict(
            username = 'TestUser',
            password = 'TestPassword',
            password2 = 'TestPassword',
            email = 'TestEmail@example.com',
            hp = ''
        ), follow_redirects = True)

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects = True)

    def logout(self):
        return self.app.get('/logout', follow_redirects = True)

class UserManagementTestCase(IdeawheelTests):
    def test_00_register(self):
        # Mismatched passwords
        result = self.app.post('/register', data = dict(
            username = 'Test',
            password = 'TestPassword',
            password2 = 'No Match',
            email = 'TestEmail@example.com',
            hp = ''
        ), follow_redirects = True)
        assert 'All fields are required' in result.data

        # Missing field
        result = self.app.post('/register', data = dict(
            username = 'Test',
            password = 'TestPassword',
            password2 = 'TestPassword',
            email = '',
            hp = ''
        ), follow_redirects = True)
        assert 'All fields are required' in result.data

        # Honeypot with data
        result = self.app.post('/register', data = dict(
            username = 'Test',
            password = 'TestPassword',
            password2 = 'TestPassword',
            email = 'TestEmail@example.com',
            hp = 'Actually a spammer'
        ), follow_redirects = True)
        assert 'All fields are required' in result.data

        # Success
        result = self.create_user()
        assert 'Logged in as <a href="/user/TestUser">TestUser</a>' \
                in result.data

        # Duplicate user
        result = self.create_user()
        assert 'That username or email is already in use' in result.data

    def test_01_login(self):
        self.create_user()

        # Success
        result = self.login('TestUser', 'TestPassword')
        assert 'Logout' in result.data

        # Bad user/pass
        result = self.login('Bad', 'User')
        assert 'Incorrect username or password' in result.data

    def test_02_logout(self):
        self.create_user()
        self.login('TestUser', 'TestPassword')

        # Success
        result = self.logout()
        assert 'Login' in result.data


if __name__ == '__main__':
    unittest.main()
