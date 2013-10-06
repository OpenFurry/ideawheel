import base64, os, random, scrypt

from flask import (
        abort,
        Blueprint,
        flash, 
        g, 
        redirect, 
        render_template, 
        request, 
        session,
        url_for,
)

from models.user import get_user

def generate_hashword(password, salt = None):
    """Generate salt and password hash for a password and optional salt."""
    if salt is None:
        salt = os.urandom(64)
    return scrypt.hash(password.encode('utf8'), salt), salt

def check_password(username, password):
    """Check Password
    
    For a given username and password, check if the given password matches the
    one stored in the database for the given user."""
    result = g.db.execute(
            'select salt, hashword from auth_users where username = ?',
            [username])
    row = result.fetchone()
    if row:
        stored_hash = base64.b64decode(row[1])
        stored_salt = base64.b64decode(row[0])
        computed_hash = generate_hashword(password, salt = stored_salt)[0]
        return is_equal_time_independent(stored_hash, computed_hash)
    return False

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
    """Log in for the session"""
    session['logged_in'] = True
    session['username'] = username


mod = Blueprint('user_management', __name__)

@mod.route('/login', methods = ['GET', 'POST'])
def login():
    next_url = request.form.get('next', request.args.get('next', '/'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_password(username, password):
            _login(username)
            return redirect(next_url)
        flash('Incorrect username or password.')
    return render_template('user_management/login.html', next_url=next_url)

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
            # TODO validate/confirm email - #29 - Makyo
            result = g.db.execute('select count(*) from auth_users where '
                    'username = ? or email = ?', [username, email])
            if result.fetchone()[0] != 0:
                flash('That username or email is already in use. Perhaps you '
                      'want to login instead?')
                return render_template('user_management/register.html')
            # 64 bytes of salt since our hash is 64 bytes long; perhaps
            # overkill but shouldn't take too long to generate
            hashword, salt = generate_hashword(password)
            g.db.execute(
                    'insert into auth_users (username, hashword, salt, email) '
                    'values (?, ?, ?, ?)',
                    [username,
                     base64.b64encode(hashword),
                     base64.b64encode(salt),
                     email])
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
    user = get_user(username)
    if not user.loaded:
        abort(404)
    return render_template('user_management/show_user.html', user = user)

@mod.route('/user/<username>/edit', methods = ['GET', 'POST'])
def edit_user(username):
    """Edit User

    Edit a user profile"""
    # Must be logged in.
    if not session.get('logged_in', False):
        abort(403)
    # Permission denied unless the user's editing themselves, or it's an admin.
    if not g.current_user.is_admin() and session['username'] != username:
        abort(403)

    user = get_user(username)
    if not user.loaded:
        abort(404)

    if request.method == 'POST':
        # Update the user with new fields so that form repopulates changed data.
        user.display_name = request.form['display_name']
        user.blurb = request.form['blurb']
        user.artist_type = request.form['artist_type']
        if 'user_type' in request.form:
            user.user_type = int(request.form['user_type'])

        # Allow password/email editing if it's the current user.
        if g.current_user.username == user.username:
            # Check old password.
            if (not request.form['password'] or not
                    check_password(user.username, request.form['password'])):
                abort(403)
            user.email = request.form['email']
            new_password = request.form['new_password']

            # Set new password if it was provided and matches confirmation;
            # otherwise, just set the email.
            if new_password:
                if new_password != request.form['new_password2']:
                    flash('New password and confirmation mismatch.')
                    return render_template('user_management/edit_user.html', 
                            user = user)
                # TODO validate/confirm email - #29 - Makyo
                hashword, salt = generate_hashword(new_password)
                g.db.execute('update auth_users set salt = ?, hashword = ?, '
                        'email = ? where username = ?', 
                        [base64.b64encode(salt), 
                         base64.b64encode(hashword), 
                         user.email, 
                         username])
            else:
                g.db.execute('update auth_users set email = ? where '
                        'username = ?', [user.email, username])

        # Set the remainder of the fields and commit.
        g.db.execute('update auth_users set display_name = ?, blurb = ?, '
                'user_type = ?, artist_type = ? where username = ?',
                [user.display_name, user.blurb, user.user_type,
                    user.artist_type, user.username])
        g.db.commit()
        flash('Profile updated!')
        return redirect(url_for('.show_user', username = username))
    return render_template('user_management/edit_user.html', user = user)
