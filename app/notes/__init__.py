from flask import Blueprint

bp = Blueprint("notes", __name__)

from app.notes import routes  # noqa: E402,F401
