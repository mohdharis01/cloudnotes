from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.notes import bp
from app.notes.forms import NoteForm
from app.extensions import db
from app.models import Note


def get_owned_note_or_404(note_id):
    note = db.session.get(Note, note_id)
    if note is None or note.user_id != current_user.id:
        abort(404)
    return note


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            title=form.title.data.strip(),
            content=form.content.data or "",
            user_id=current_user.id,
        )
        db.session.add(note)
        db.session.commit()
        flash("Note created.", "success")
        return redirect(url_for("notes.detail", note_id=note.id))
    return render_template("notes/form.html", form=form, heading="New note")


@bp.route("/<int:note_id>")
@login_required
def detail(note_id):
    note = get_owned_note_or_404(note_id)
    return render_template("notes/detail.html", note=note)


@bp.route("/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit(note_id):
    note = get_owned_note_or_404(note_id)
    form = NoteForm(obj=note)
    if form.validate_on_submit():
        note.title = form.title.data.strip()
        note.content = form.content.data or ""
        db.session.commit()
        flash("Note updated.", "success")
        return redirect(url_for("notes.detail", note_id=note.id))
    return render_template("notes/form.html", form=form, heading="Edit note")


@bp.route("/<int:note_id>/delete", methods=["POST"])
@login_required
def delete(note_id):
    note = get_owned_note_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    flash("Note deleted.", "info")
    return redirect(url_for("main.dashboard"))
