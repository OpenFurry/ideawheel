import scrypt, random, base64, os

from flask import (
        Blueprint,
        flash, 
        g, 
        redirect, 
        render_template, 
        request, 
        session
)

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
            stored_hash = base64.b64decode(row[1])
            stored_salt = base64.b64decode(row[0])
            computed_hash = scrypt.hash(password.encode('utf8'), stored_salt)
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
    session['logged_in'] = False
    session['username'] = None
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
            # 64 bytes of salt since our hash is 64 bytes long; perhaps
            # overkill but shouldn't take too long to generate
            salt = os.urandom(64)
            hashword = scrypt.hash(password.encode('utf8'), salt)
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
    pass

@mod.route('/user/<username>/edit')
def edit_user(username):
    """Edit User

    Edit a user profile"""
    pass
