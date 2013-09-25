from flask import (
        Blueprint
)

mod = Blueprint('idea_management', __name__)

@mod.route('/stub/create', methods = ['GET', 'POST'])
def create_stub():
    """Create Stub (staff only)

    Create a new idea stub."""
    pass

@mod.route('/stub/<stub_id>')
def view_stub():
    """View Stub

    View a stub and all of the ideas of which it is a part."""
    pass

@mod.route('/stub/<stub_id>/retire', methods = ['GET', 'POST'])
def retire_stub():
    """Retire Stub (staff only)

    Prevent a stub from showing up in the random display and from being used in
    any ideas."""
    pass

@mod.route('/stub/<stub_id>/unretire', methods = ['GET', 'POST'])
def unretire_stub():
    """Unretire Stub (staff only)

    Remove the retired status from a stub."""
    pass
