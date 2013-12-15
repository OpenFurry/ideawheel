from flask import (
    Blueprint,
)

mod = Blueprint('idea_building', __name__)


@mod.route('/idea')
def random_stub():
    """Random Stub

    Get a random idea stub to show to the user. If the stub has been
    used in an idea already, provide a link."""
    pass


@mod.route('/idea/create', methods=['POST'])
def create_idea():
    """Create Idea

    Store an idea as a page so that creations can be posted to it."""
    pass


@mod.route('/pin/<int:stub_id>')
def pin_stub(stub_id):
    """Pin Stub

    Pin a stub so that idea stubs can be strung together into something
    coherent."""
    pass
