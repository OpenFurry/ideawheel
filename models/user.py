from flask import g

class User:
    """User

    An object representing a user."""
    def __init__(self, username = None, email = None, display_name = None,
            blurb = None, artist_type = None, user_type = None):
        self.loaded = False
        self.username = username
        self.email = email
        self.display_name = display_name
        self.blurb = blurb
        self.artist_type = artist_type
        self.user_type = user_type

        if self.username and self.email and self.user_type is not None:
            self.loaded = True

    def is_staff(self):
        if self.loaded:
            return self.user_type >= 1
        return None

    def is_admin(self):
        if self.loaded:
            return self.user_type == 2
        return None

def get_user(username):
    """Return a populated User object, given a username."""
    result = g.db.execute('select email, display_name, blurb, artist_type, '
            'user_type from auth_users where username = ?',
            [username])
    row = result.fetchone()
    if not row:
        return User(username = username)
    return User(username = username, email = row[0], display_name = row[1],
            blurb = row[2], artist_type = row[3], user_type = row[4])
