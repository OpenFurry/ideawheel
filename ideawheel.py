import datetime, hashlib, inspect, os, random, sqlite3, sys

from flask import (
        Flask, 
        abort, 
        flash, 
        g, 
        redirect, 
        render_template, 
        request, 
        session
)

# Configuration
DATABASE = os.path.join(
        os.path.dirname(
            os.path.abspath(
                inspect.getfile(inspect.currentframe()))), 
        'ideawheel.db')
SECRET_KEY = os.urandom(12)
DEBUG = True

# App construction
app = Flask(__name__)
app.config.from_object(__name__)

# App helpers
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    from contextlib import closing
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()
    if not app.config['TESTING'] and request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

def generate_csrf_token():
    if not app.config['TESTING'] and '_csrf_token' not in session:
        session['_csrf_token'] = hashlib.sha1(os.urandom(40)).hexdigest()
    return session.get('_csrf_token', '')

app.jinja_env.globals['csrf_token'] = generate_csrf_token 

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# View functions
@app.route('/')
def default():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
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
            if hashlib.sha1(unicode(row[0]) + password).hexdigest() == row[1]:
                _login(username)
                return redirect(next_url)
        flash('Incorrect username or password.')
    return render_template('login.html', next_url=next_url)

def _login(username):
    session['logged_in'] = True
    session['username'] = username

@app.route('/logout')
def logout():
    session['logged_in'] = False
    session['username'] = None
    flash('Successfully logged out')
    return redirect('/')

@app.route('/register', methods = ['GET', 'POST'])
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
                return render_template('register.html')
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
    return render_template('register.html')

@app.route('/idea')
def random_idea():
    """Random Idea

    Get a random idea stub to show to the user. If the stub has been
    used in an idea already, provide a link."""
    pass

@app.route('/idea/create', methods = ['POST'])
def create_idea():
    """Create Idea

    Store an idea as a page so that creations can be posted to it."""
    pass

@app.route('/idea/<int:idea_id>')
def read_idea(idea_id):
    """Read Idea

    Show an idea and all things posted to it"""
    pass

@app.route('/pin/<int:idea_id>')
def pin_idea(idea_id):
    """Pin Idea
    
    Pin an idea so that idea snippets can be strung together into something
    coherent."""
    pass

@app.route('/ideas')
def list_ideas():
    """List Ideas

    List all created ideas."""
    pass

@app.route('/user/<username>')
def show_user(username):
    """Show User

    Show all ideas that a user as created or posted to; if the user is logged
    in, then show the ideas they have pinned"""
    pass

@app.route('/user/<username>/edit')
def edit_user(username):
    """Edit User

    Edit a user profile"""
    pass

@app.route('/idea/<int:idea_id>/post', methods = ['POST'])
def create_post(idea_id):
    """Create Post

    Post content to an idea."""
    pass

@app.route('/post/<int:post_id>')
def read_post(post_id):
    """Read Post

    Read a post attached to an idea."""
    pass

@app.route('/post/<int:post_id>/edit', methods = ['GET', 'POST'])
def edit_post(post_id):
    """Edit Post

    Edit (or delete) a post attached to an idea."""
    pass

if __name__ == '__main__':
    app.run()
