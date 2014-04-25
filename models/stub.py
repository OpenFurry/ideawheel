from flask import g


class Stub:
    """Stub

    A small portion of an idea. Each stub is a small sentence fragment, image,
    or phrase that can be assembled to create an idea."""
    def __init__(self, stub_id=None, text=None, link=None):
        self.stub_id = stub_id
        self.text = text
        self.link = link


def create_stub(stub_text, link=None):
    """Create a new stub with the given text"""
    result = g.db.execute(
        'insert into idea_stubs (stub, link) values (?, ?)',
        [stub_text, link]
    )
    added_stub_id = result.lastrowid
    g.db.commit()

    return Stub(stub_id=added_stub_id, text=stub_text)


def get_random_stub():
    """Get a random stub"""
    # Naive approach: Rely on sqlite to do the randomness for now since
    # it's easy to implement and relatively performant.
    # What we probably want isn't to call this multiple times but to have
    # something that picks N stubs without replacement.
    result = g.db.execute(
        'SELECT id, stub, link FROM idea_stubs '
        'WHERE id >= (ABS(RANDOM()) % (SELECT MAX(id) FROM idea_stubs) + 1) '
        'LIMIT 1')
    row = result.fetchone()
    return Stub(stub_id=row[0], text=row[1], link=row[2])


def get_stub(stub_id):
    """Get a particular stub specified by stub_id"""
    result = g.db.execute('SELECT id, stub, link FROM idea_stubs WHERE id = ?',
                          [stub_id])
    row = result.fetchone()

    if not row:
        return None

    return Stub(stub_id=row[0], text=row[1], link=row[2])
