from flask import render_template, request
from flask_login import login_required, current_user
from sqlalchemy import or_

from app.main import bp
from app.extensions import db
from app.models import Note


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
