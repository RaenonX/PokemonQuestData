import os
from urllib.parse import urlparse, urljoin
from functools import wraps

from flask import (
    Blueprint, 
    render_template, request, session, current_app, redirect, url_for
)
import pymongo

from data.thirdparty import google_identity

mongo = pymongo.MongoClient(os.environ["MONGO_URI"])

gi = google_identity(mongo)

frontend_user = Blueprint("frontend_user", __name__)
    
@frontend_user.route("/user-verify", methods=["GET"])
def user_verify():
    prev = request.args.get('prev')
    is_safe = is_safe_url(prev)
    return render_template("user_verify.html", prev=prev if is_safe and prev != "" else url_for("frontend.index"))

@frontend_user.route("/user-verify", methods=["POST"])
def user_verify_post():
    registration_succeed = gi.register_user(request.form["email"], request.form["token"], session)
    
    return "PASS" if registration_succeed else "註冊失敗。"

def require_login(prev, **kwargs_url):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(*args):
            if gi.user_exists(session=session):
                return func(*args)
            else:
                return redirect(url_for("frontend_user.user_verify", prev=url_for(prev, **kwargs_url)))
        return func_wrapper
    return func_decorator

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc