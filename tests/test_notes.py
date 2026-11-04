from app.extensions import db
from app.models import Note


def note_id_by_title(app, title):
    with app.app_context():
        return db.session.scalar(db.select(Note.id).where(Note.title == title))


def create_note(client, title, content="body text"):
    return client.post("/notes/new", data={"title": title, "content": content},
                       follow_redirects=True)


def test_create_and_view_note(app, make_client):
    c = make_client("alice", "alice@example.com")
    r = create_note(c, "My first note", "hello world")
    assert b"Note created" in r.data
    assert b"hello world" in r.data


def test_create_note_requires_title(make_client):
    c = make_client("alice", "alice@example.com")
    r = create_note(c, "")
    assert b"Note created" not in r.data


def test_edit_note(app, make_client):
    c = make_client("alice", "alice@example.com")
    create_note(c, "Old title")
    nid = note_id_by_title(app, "Old title")
    r = c.post(f"/notes/{nid}/edit", data={"title": "New title", "content": "x"},
               follow_redirects=True)
    assert b"New title" in r.data


def test_delete_note(app, make_client):
    c = make_client("alice", "alice@example.com")
    create_note(c, "To delete")
    nid = note_id_by_title(app, "To delete")
    c.post(f"/notes/{nid}/delete")
    assert c.get(f"/notes/{nid}").status_code == 404


def test_other_user_cannot_access_note(app, make_client):
    alice = make_client("alice", "alice@example.com")
    bob = make_client("bob", "bob@example.com")
    create_note(alice, "Secret")
    nid = note_id_by_title(app, "Secret")

    assert bob.get(f"/notes/{nid}").status_code == 404
    assert bob.get(f"/notes/{nid}/edit").status_code == 404
    assert bob.post(f"/notes/{nid}/edit",
                    data={"title": "Hacked", "content": "x"}).status_code == 404
    assert bob.post(f"/notes/{nid}/delete").status_code == 404

    assert note_id_by_title(app, "Secret") == nid
    assert note_id_by_title(app, "Hacked") is None


def test_anonymous_cannot_access_note(app, make_client, client):
    alice = make_client("alice", "alice@example.com")
    create_note(alice, "Private")
    nid = note_id_by_title(app, "Private")
    r = client.get(f"/notes/{nid}")
    assert r.status_code == 302
    assert "/auth/login" in r.headers["Location"]


def test_dashboard_shows_only_own_notes(make_client):
    alice = make_client("alice", "alice@example.com")
    bob = make_client("bob", "bob@example.com")
    create_note(alice, "Alice note")
    create_note(bob, "Bob note")
    r = alice.get("/dashboard")
    assert b"Alice note" in r.data
    assert b"Bob note" not in r.data


def test_search_filters_notes(make_client):
    c = make_client("alice", "alice@example.com")
    create_note(c, "Python tips")
    create_note(c, "Grocery list")
    r = c.get("/dashboard?q=python")
    assert b"Python tips" in r.data
    assert b"Grocery list" not in r.data


def test_note_content_is_escaped(app, make_client):
    c = make_client("alice", "alice@example.com")
    create_note(c, "XSS test", "<script>alert(1)</script>")
    nid = note_id_by_title(app, "XSS test")
    r = c.get(f"/notes/{nid}")
    assert b"<script>alert(1)</script>" not in r.data
    assert b"&lt;script&gt;" in r.data
