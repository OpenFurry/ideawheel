from flask import Flask

app = Flask(__name__)

@app.route('/')
def default():
    pass

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        pass
    else:
        pass

@app.route('/logout')
def logout():
    pass

@app.route('/idea')
def random_idea():
    """Random Idea

    Get a random idea (or snippet) to show to the user. If the idea has been
    created already, provide a link."""
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
    """ Pin Idea
    
    Pin an idea so that idea snippets can be strung together into somethign
    coherent."""
    pass

@app.route('/ideas')
def list_ideas():
    """List Ideas

    List all created ideas."""
    pass

@app.route('/user/<username>/ideas')
def ideas_for_user(username):
    """Ideas for User

    Show all ideas that a user as created or posted to; if the user is logged
    in, then show the ideas they have pinned"""
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
