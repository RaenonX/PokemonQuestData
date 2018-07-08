from flask import Blueprint

dummy = Blueprint("dummy", __name__)

@dummy.route("/prevent-sleep")
def prevent_sleep():
    return "PINGED"