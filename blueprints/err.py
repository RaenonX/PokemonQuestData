from flask import Blueprint, flash, redirect, url_for

err = Blueprint("err", __name__)

@err.app_errorhandler(404)
def page_not_found(error):
    flash("404 - 因目前網頁尚未建置完畢而找不到網頁，造成不便還請見諒。", category='error')
    return redirect(url_for("frontend.index"))

@err.app_errorhandler(500)
def page_not_found(error):
    flash("500 - 伺服器內部發生錯誤。", category='error')
    return redirect(url_for("frontend.index"))