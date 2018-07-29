import os
from urllib.parse import urlparse, urljoin
from functools import wraps

from flask import (
    Blueprint, 
    render_template, request, session, current_app, redirect, url_for, flash
)

from .nav import render_template
from ._objs import *

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

def require_login_return_msg(err_msg, **kwargs_url):
    def func_decorator(func):
        @wraps(func)
        def func_wrapper(*args):
            if gi.user_exists(session=session):
                return func(*args)
            else:
                return err_msg
        return func_wrapper
    return func_decorator

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@frontend_user.route("/submit-result", methods=["GET"])
@require_login("frontend_user.submit_result")
def submit_result():
    return render_template('submit_result.html', 
                           poke_choices=pkc.get_pokemon_choices(False), 
                           recipe_choices=rcc.get_recipe_choices(), 
                           quality_choices=RecipeQuality.get_choices())

@frontend_user.route("/submit-result", methods=["POST"])
@require_login("frontend_user.submit_result")
def submit_result_post():
    acknowledged = cdm.add_record(request.form["pokemon"], request.form["recipe"], request.form["quality"], session[identity_entry_uid_key])

    submit_more = request.form["more"] == "TRUE"
    recaptcha_pass = gr.verify(request.form["g-recaptcha-response"])

    if acknowledged and recaptcha_pass:
        flash("感謝您協助提供資料！")
        return redirect(url_for("frontend_user.submit_result") if submit_more else url_for(".index"))
    else:
        if not recaptcha_pass:
            flash("reCAPTCHA驗證失敗。", category="warning")
        else:
            flash("資料提交失敗。請檢查提交的資料是否正確。", category="warning")
        return redirect(url_for("frontend_user.submit_result"))

@frontend_user.route("/report", methods=["POST"])
@require_login_return_msg("請先登記身分再提報可疑資料。")
def report_suspicious():
    data_id = request.form["dataId"]
    report_result = cdm.report_suspicious(data_id, session[identity_entry_uid_key])

    if report_result:
        flash("資料舉報成功！")
        msg = Message("Suspicious Data Report", recipients=["maplestory0710@gmail.com"])
        msg.body = "An entry of data has been reported suspicious. {} Recommended to review before {}".format(data_id, datetime.utcnow() + timedelta(days=2))
        current_app.config["MAIL_INSTANCE"].send(msg)
        return "PASS"
    else:
        flash("資料舉報失敗。(資料ID: {})".format(data_id))
        return "FAIL"
    
@frontend_user.route("/del-record", methods=["POST"])
@require_login_return_msg("登記身分並記錄開鍋結果才可以使用此功能。")
def delete_record_user():
    data_id = request.form["dataId"]
    deletion_succeed = cdm.del_record(data_id)

    if deletion_succeed:
        flash("資料刪除成功！", category='success')
        return "PASS"
    else:
        flash("資料刪除失敗。(資料ID: {})".format(data_id), category='danger')
        return "FAIL"

@frontend_user.route("/view-poke", methods=["GET"])
@require_login(".view_owned_pokemon")
def view_owned_pokemon():
    return render_template("pokemanage/view_pokemon.html", 
                           records=pm.get_records_of_user(session[identity_entry_uid_key]), 
                           bingo_trans=bgc.get_bingo_description)

@frontend_user.route("/add-poke", methods=["GET"])
@require_login("frontend_user.submit_owned_pokemon")
def submit_owned_pokemon():
    pkms = pkc.get_all_pokemons()

    return render_template("pokemanage/submit_pokemon.html", pokemons=pkms)

@frontend_user.route("/add-poke", methods=["POST"])
@require_login("frontend_user.submit_owned_pokemon")
def submit_owned_pokemon_post():
    print(request.form)
    failed = False

    for i in range(1, int(request.form["count"]) + 1):
        i = str(i)

        poke_id = request.form["pokemon" + i]
        poke_name = request.form["pokename" + i]

        bingo_arr = [int(request.form["bingo1_" + i]), int(request.form["bingo2_" + i]), int(request.form["bingo3_" + i])]
        
        skill_arr = [int(request.form["skill1_" + i])]
        skill2_id = int(request.form["skill2_" + i])
        if skill2_id > 0:
            skill_arr.append(skill2_id)
            
        slotHp = int(request.form["slotHp" + i] if request.form["slotHp" + i] else -1)
        slotAtk = int(request.form["slotAtk" + i] if request.form["slotAtk" + i] else -1)
        slotDuo = int(request.form["slotDuo" + i] if request.form["slotDuo" + i] else -1)

        hp = int(request.form["hp" + i] if request.form["hp" + i] else -1)
        atk = int(request.form["atk" + i] if request.form["atk" + i] else -1)
        lv = int(request.form["lv" + i] if request.form["lv" + i] else -1)

        failed = pm.insert_record(session[identity_entry_uid_key], poke_id, poke_name, bingo_arr, skill_arr, slotHp, slotAtk, slotDuo, hp, atk, lv) or failed

    if failed:
        flash("資料提交成功！")
        return redirect(url_for("frontend_user.view_owned_pokemon"))
    else:
        flash("資料提交失敗。", category='danger')
        return redirect(url_for("frontend_user.submit_owned_pokemon")) 