from flask import (
        Blueprint
)

mod = Blueprint('content_posting', __name__)

@mod.route('/idea/<int:idea_id>/post', methods = ['POST'])
def create_post(idea_id):
    """Create Post

    Post content to an idea."""
    pass

@mod.route('/post/<int:post_id>')
def read_post(post_id):
    """Read Post

    Read a post attached to an idea."""
    pass

@mod.route('/post/<int:post_id>/edit', methods = ['GET', 'POST'])
def edit_post(post_id):
    """Edit Post

    Edit (or delete) a post attached to an idea."""
    pass

@mod.route('/ideas')
def list_ideas():
    """List Ideas

    List all created ideas."""
    pass

@mod.route('/idea/<int:idea_id>')
def read_idea(idea_id):
    """Read Idea

    Show an idea and all things posted to it"""
    pass
