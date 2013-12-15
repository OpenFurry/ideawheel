from flask import (
    Blueprint,
    session,
    abort,
    render_template,
    g,
    request,
    flash,
    redirect,
    url_for,
)

import models.stub

mod = Blueprint('idea_management', __name__)


@mod.route('/stub/create', methods=['GET', 'POST'])
def create_stub():
    """Create Stub (staff only)

    Create a new idea stub."""
    # Must be a logged in staff member
    if not (session.get('logged_in', False) and g.current_user.is_staff()):
        abort(403)

    if request.method == 'POST':
        stub_text = request.form['stub_text']
        # TODO input validation/sanitation?
        created_stub = models.stub.create_stub(stub_text)

        flash('Stub created!')
        return redirect(url_for('.view_stub', stub_id=created_stub.stub_id))

    return render_template('idea_management/create_stub.html')


@mod.route('/stub/<stub_id>')
def view_stub(stub_id):
    """View Stub

    View a stub and all of the ideas of which it is a part."""
    stub = models.stub.get_stub(stub_id)
    if stub is None:
        abort(404)
    return render_template('idea_management/view_stub.html')


@mod.route('/stub/<stub_id>/retire', methods=['GET', 'POST'])
def retire_stub():
    """Retire Stub (staff only)

    Prevent a stub from showing up in the random display and from being used in
    any ideas."""
    pass


@mod.route('/stub/<stub_id>/unretire', methods=['GET', 'POST'])
def unretire_stub():
    """Unretire Stub (staff only)

    Remove the retired status from a stub."""
    pass
