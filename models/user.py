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
            return self.user_type == 1
        return None

    def is_admin(self):
        if self.loaded:
            return self.user_type == 2
        return None
