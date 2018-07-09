from flask import Blueprint, flash, redirect, url_for, request

err = Blueprint("err", __name__)

@err.app_errorhandler(404)
def page_not_found(error):
    flash("404 - 找不到網頁。(來自{})".format(request.referrer), category='error')
    return redirect(url_for("frontend.index"))

@err.app_errorhandler(500)
def internal_error(error):
    flash("500 - 伺服器內部發生錯誤。(來自{})".format(request.referrer), category='error')
    return redirect(url_for("frontend.index"))