from flask import Blueprint, send_from_directory

static = Blueprint("static", __name__)


@static.route("/ads.txt")
def ads_txt():
    return send_from_directory("static", "ads.txt")
