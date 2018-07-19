### https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n
### http://jinja.pocoo.org/docs/2.10/extensions/
### https://stackoverflow.com/questions/34579316/flask-babel-how-to-translate-variables
### https://stackoverflow.com/questions/216616/how-to-create-strings-containing-double-quotes-in-excel-formulas

import os
from datetime import datetime, timedelta

from flask import (
    Blueprint, 
    flash, redirect, url_for, request, current_app, session
)
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_mail import Message
from markupsafe import escape
import pymongo

from data import RecipeQuality, PokeType
from data.mongo import (
    cook_data_manager,
    pokemon_collection, pokemon_skill_collection, pokemon_bingo_collection, recipe_collection, 
    site_log_manager, pokemon_integrator,
    official_probability
)
from data.thirdparty import google_analytics, google_identity, identity_entry_uid_key

from .nav import nav, render_template
from .frontend_user import require_login, require_login_return_msg

frontend = Blueprint("frontend", __name__)

mongo = pymongo.MongoClient(os.environ["MONGO_URI"])

cdm = cook_data_manager(mongo)

pkc = pokemon_collection(mongo)
rcc = recipe_collection(mongo)
skc = pokemon_skill_collection(mongo)
bgc = pokemon_bingo_collection(mongo, pkc)

pi = pokemon_integrator(pkc, skc, bgc)

op = official_probability(mongo)

slm = site_log_manager(mongo)
ga = google_analytics()
gi = google_identity(mongo)

@frontend.route("/")
def index():
    return render_template("index.html", 
                           recent=cdm.get_last(count=10), 
                           count=cdm.get_count(),
                           identity_count=gi.get_count(),
                           site_log=slm.get_last(7),
                           hotpages=ga.get_top_unique_pageviews_by_path(),
                           site_root=os.environ["APP_ROOT_URL"])

@frontend.route("/recent")
def recent_new_data():
    start = int(request.args.get('start', 0))
    result_count = 100

    return render_template("recent_data.html", 
                           data=cdm.get_last(start=start, count=result_count),
                           start=start,
                           result_count=result_count,
                           recent_cook=cdm.get_count_last_7_days(),
                           most_add=cdm.get_top_20_provider_ids())

@frontend.route("/recent-user/<uid>")
@frontend.route("/recent-user/")
def recent_new_data_by_user(uid=""):
    if uid is None or uid == "":
        uid = session.get(identity_entry_uid_key, "")

    if uid is None or uid == "":
        flash("使用者ID獲取失敗，改為顯示最新開鍋紀錄。登記至少一筆開鍋紀錄即可查看自己的開鍋結果。")
        return redirect(url_for(".recent_new_data"))
    else:
        start = int(request.args.get('start', 0))
        result_count = 100

        return render_template("recent_data_user.html", 
                               data=cdm.get_entries_by_adder_uid(uid, start, result_count),
                               start=start,
                               result_count=result_count,
                               user_owned=(uid == session.get(identity_entry_uid_key, "")))
    
@frontend.route("/del-record", methods=["POST"])
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
    
@frontend.route("/poke-profile")
def pokemon_profile_index():
    return render_template("poke_list.html", 
                           pokedata=pkc.get_all_pokemons(),
                           poketype=PokeType,
                           next_endpoint=".pokemon_profile_result",
                           title="查詢精靈資料")

@frontend.route("/poke-profile/<int:id>")
def pokemon_profile_result(id):
    return render_template("poke_profile.html", 
                           profile=pi.get_pokemon_profile(id))

@frontend.route("/poke-skill")
def poke_skill_index():
    return render_template("skill_list.html", skill_data=skc.get_all_skills())

@frontend.route("/poke-skill/<int:id>")
def poke_skill_result(id):
    return render_template("skill_result.html", 
                           pokes=pkc.get_pokemons_by_skill_owned(id),
                           skill=skc.get_skill_data(id))

@frontend.route("/find-recipe")
def find_recipe_index():
    return render_template("poke_list.html", 
                           pokedata=pkc.get_all_pokemons(False),
                           poketype=PokeType,
                           next_endpoint=".find_recipe_result",
                           title="從精靈查食譜",
                           mesasage="煮鍋時，只能做出第一型態的精靈。所有進化過的精靈都無法藉由煮鍋獲得。")

@frontend.route("/find-recipe/<int:id>")
def find_recipe_result(id):
    return render_template("recipe_result.html", 
                           result=cdm.get_cook_data_by_pokemon_id(id),
                           off_prob=op.get_data_by_pokemon_id(id))
    
@frontend.route("/find-pokemon")
def find_pokemon_index():
    return render_template("recipe_list.html", recipedata=rcc.get_all_recipes())

@frontend.route("/find-pokemon/<int:id>")
def find_pokemon_result(id):
    return render_template("poke_result.html", 
                           result=cdm.get_poke_data_by_recipe_id(id),
                           off_prob=op.get_data_by_recipe_id(id))

@frontend.route("/submit-result", methods=["GET"])
@require_login(".submit_result")
def submit_result():
    return render_template('submit_result.html', 
                           poke_choices=pkc.get_pokemon_choices(False), 
                           recipe_choices=rcc.get_recipe_choices(), 
                           quality_choices=RecipeQuality.get_choices())

@frontend.route("/submit-result", methods=["POST"])
@require_login(".submit_result")
def submit_result_post():
    acknowledged = cdm.add_record(request.form["pokemon"], request.form["recipe"], request.form["quality"], session[identity_entry_uid_key])
    if acknowledged:
        flash("感謝您協助提供資料！")
        return redirect(url_for(".index"))
    else:
        flash("資料提交失敗。請檢查提交的資料是否正確。", category="warning")
        return redirect(url_for(".submit_result"))

@frontend.route("/report", methods=["POST"])
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

@frontend.route("/about")
def about():
    return render_template("about.html")

@frontend.route("/dz")
def dark_zone():
    return render_template("dz.html")