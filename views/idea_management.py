from flask import (
        Blueprint,
        session,
        abort,
        render_template,
        g,
        request,
        flash,
        redirect,
        url_for
)

mod = Blueprint('idea_management', __name__)

@mod.route('/stub/create', methods = ['GET', 'POST'])
def create_stub():
    """Create Stub (staff only)

    Create a new idea stub."""
    # Must be a logged in admin
    if not (session.get('logged_in', False) and g.current_user.is_admin()):
        abort(403)

    if request.method == 'POST':
        stub = request.form['stub_text']

        result = g.db.execute(
            'insert into idea_stubs (stub) values (?)',
            [stub]
        )
        stub_id = result.lastrowid
        g.db.commit()

        flash('Stub created!')
        return redirect(url_for('.view_stub', stub_id = stub_id))
    
    return render_template('idea_management/create_stub.html')

@mod.route('/stub/<stub_id>')
def view_stub(stub_id):
    """View Stub

    View a stub and all of the ideas of which it is a part."""
    return render_template('idea_management/view_stub.html')

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
