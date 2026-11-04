from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import or_

from app.main import bp
from app.main.forms import GroupForm
from app.extensions import db
from app.models import Note, Group


def get_owned_group_or_404(group_id):
    group = db.session.get(Group, group_id)
    if group is None or group.user_id != current_user.id:
        abort(404)
    return group


@bp.app_context_processor
def inject_sidebar_groups():
    if not current_user.is_authenticated:
        return {"sidebar_groups": []}
    stmt = db.select(Group).where(Group.user_id == current_user.id).order_by(Group.name)
    return {"sidebar_groups": db.session.scalars(stmt).all()}


@bp.route("/")
def index():
    return render_template("main/index.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    q = request.args.get("q", "").strip()
    stmt = db.select(Note).where(Note.user_id == current_user.id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Note.title.ilike(like), Note.content.ilike(like)))
    notes = db.session.scalars(stmt.order_by(Note.updated_at.desc())).all()
    return render_template("main/dashboard.html", notes=notes, q=q)


@bp.route("/groups/new", methods=["GET", "POST"])
@login_required
def group_new():
    form = GroupForm()
    if form.validate_on_submit():
        group = Group(
            name=form.name.data.strip(),
            color=form.color.data,
            user_id=current_user.id,
        )
        db.session.add(group)
        db.session.commit()
        flash("Group created.", "success")
        return redirect(url_for("main.group_detail", group_id=group.id))
    return render_template("groups/form.html", form=form, heading="New group")


@bp.route("/groups/<int:group_id>")
@login_required
def group_detail(group_id):
    group = get_owned_group_or_404(group_id)
    stmt = (
        db.select(Note)
        .where(Note.user_id == current_user.id, Note.group_id == group.id)
        .order_by(Note.updated_at.desc())
    )
    notes = db.session.scalars(stmt).all()
    return render_template("groups/detail.html", group=group, notes=notes)


@bp.route("/groups/<int:group_id>/edit", methods=["GET", "POST"])
@login_required
def group_edit(group_id):
    group = get_owned_group_or_404(group_id)
    form = GroupForm(obj=group)
    if form.validate_on_submit():
        group.name = form.name.data.strip()
        group.color = form.color.data
        db.session.commit()
        flash("Group updated.", "success")
        return redirect(url_for("main.group_detail", group_id=group.id))
    return render_template("groups/form.html", form=form, heading="Edit group")


@bp.route("/groups/<int:group_id>/delete", methods=["POST"])
@login_required
def group_delete(group_id):
    group = get_owned_group_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    flash("Group deleted. Its notes were kept.", "info")
    return redirect(url_for("main.dashboard"))
