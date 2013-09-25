import hashlib, random

from flask import (
        abort,
        Blueprint,
        flash, 
        g, 
        redirect, 
        render_template, 
        request, 
        session,
        url_for
)


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

def get_user(username):
    result = g.db.execute('select email, display_name, blurb, artist_type, '
            'user_type from auth_users where username = ?',
            [username])
    row = result.fetchone()
    if not row:
        abort(404)
    return User(username = username, email = row[0], display_name = row[1],
            blurb = row[2], artist_type = row[3], user_type = row[4])


mod = Blueprint('user_management', __name__)

@mod.route('/login', methods = ['GET', 'POST'])
def login():
    next_url = request.form.get('next', request.args.get('next', '/'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        result = g.db.execute(
                'select salt, hashword from auth_users where username = ?',
                [username])
        row = result.fetchone()
        if row:
            stored_hash = row[1]
            computed_hash = hashlib.sha1(unicode(row[0]) + password).hexdigest()
            if is_equal_time_independent(stored_hash, computed_hash):
                _login(username)
                return redirect(next_url)
        flash('Incorrect username or password.')
    return render_template('user_management/login.html', next_url=next_url)

def is_equal_time_independent(a, b):
    """Determine if two strings are equal in constant time.

    Normally we're quite happy if string equality comparisons early out on
    the first mismatch. However, when we use compare security-sensitive data
    like password hashes, breaking early can expose timing attacks which help
    leak information about what a valid hash would be.

    For more information on this class of attacks, see, for example:
    http://codahale.com/a-lesson-in-timing-attacks/
    http://rdist.root.org/2010/01/07/timing-independent-array-comparison/
    http://www.cs.rice.edu/~dwallach/pub/crosby-timing2009.pdf
    """
    # Implementation is per Nate Lawson's timing-independent compare
    # suggestion for Keyczar, available here:
    # https://groups.google.com/forum/#!topic/keyczar-discuss/VXHsoJSLKhM
    if len(a) != len(b):
        return False

    result = 0
    for x, y in zip (a, b):
        result |= ord(x) ^ ord(y)

    return result == 0

def _login(username):
    session['logged_in'] = True
    session['username'] = username

@mod.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Successfully logged out')
    return redirect('/')

@mod.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        if (not request.form['username'] or not request.form['password']
                or not request.form['email'] or request.form['hp']
                or request.form['password'] != request.form['password2']):
            flash('All fields are required.')
        else:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            result = g.db.execute('select count(*) from auth_users where '
                    'username = ? or email = ?', [username, email])
            if result.fetchone()[0] != 0:
                flash('That username or email is already in use. Perhaps you '
                      'want to login instead?')
                return render_template('user_management/register.html')
            salt = random.randint(1000, 9999)
            hashword = hashlib.sha1(unicode(salt) + password).hexdigest()
            g.db.execute(
                    'insert into auth_users (username, hashword, salt, email) '
                    'values (?, ?, ?, ?)',
                    [username, hashword, salt, email])
            g.db.commit()
            _login(username)
            flash('Thank you for registering! You are now logged in.')
            return redirect('/')
    return render_template('user_management/register.html')

@mod.route('/user/<username>')
def show_user(username):
    """Show User

    Show all ideas that a user as created or posted to; if the user is logged
    in, then show the stubs they have pinned"""
    return render_template('user_management/show_user.html', user = get_user(username))

@mod.route('/user/<username>/edit', methods = ['GET', 'POST'])
def edit_user(username):
    """Edit User

    Edit a user profile"""
    if (not session.get('logged_in', False) and (session['username'] != username
            or not g.current_user.is_admin())):
        abort(403)
    user = get_user(username)
    if request.method == 'POST':
        if g.current_user.username == user.username:
            # check password
            # set password, email separately if need be
        # update other fields
        return redirect(url_for('.show_user', username = username))
    return render_template('user_management/edit_user.html', user = user)
