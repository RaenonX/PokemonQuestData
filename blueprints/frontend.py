### Use elements to get pokes
### Handle case of evolved poke
### Add statistics page

import os

from flask import (
    Blueprint, 
    render_template, flash, redirect, url_for, request, current_app, session
)
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from markupsafe import escape
import pymongo

from data import RecipeQuality, PokeType
from data.mongo import cook_data_manager, pokemon_collection, recipe_collection, site_log_manager
from data.thirdparty import google_analytics, google_identity, identity_entry_uid_key

from .nav import nav

frontend = Blueprint("frontend", __name__)

mongo = pymongo.MongoClient(os.environ["MONGO_URI"])

cdm = cook_data_manager(mongo)
pkc = pokemon_collection(mongo)
rcc = recipe_collection(mongo)

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
                           result_count=result_count)

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
                               result_count=result_count)
    
@frontend.route("/find-recipe")
def find_recipe_index():
    return render_template("poke_list.html", 
                           pokedata=pkc.get_all_pokemons(False),
                           poketype=PokeType)

@frontend.route("/find-recipe/<int:id>")
def find_recipe(id):
    return render_template("recipe_result.html", result=cdm.get_cook_data_by_pokemon_id(id))
    
@frontend.route("/find-pokemon")
def find_pokemon_index():
    return render_template("recipe_list.html", recipedata=mongo.dict.recipe.find().sort([("id", pymongo.ASCENDING)]))

@frontend.route("/find-pokemon/<int:id>")
def find_pokemon(id):
    return render_template("poke_result.html", result=cdm.get_poke_data_by_recipe_id(id))

@frontend.route("/submit-result", methods=["GET"])
def submit_result():
    if gi.user_exists(session=session):
        return render_template('submit_result.html', 
                           poke_choices=pkc.get_pokemon_choices(False), 
                           recipe_choices=rcc.get_recipe_choices(), 
                           quality_choices=RecipeQuality.get_choices())
    else:
        return redirect(url_for(".user_verify", prev=url_for(".submit_result")))
    
@frontend.route("/user-verify", methods=["GET"])
def user_verify():
    return render_template("user_verify.html", prev=request.args.get('prev'))

@frontend.route("/user-verify", methods=["POST"])
def user_verify_post():
    registration_succeed = gi.register_user(request.form["email"], request.form["token"], session)
    
    return "PASS" if registration_succeed else "註冊失敗。"

@frontend.route("/submit-result", methods=["POST"])
def submit_result_post():
    if identity_entry_uid_key in session:
        acknowledged = cdm.add_record(request.form["recipe"], request.form["quality"], request.form["pokemon"], session [identity_entry_uid_key])
        if acknowledged:
            flash("感謝您協助提供資料！")
            return redirect(url_for(".index"))
        else:
            flash("資料提交失敗。", category="warning")
            return redirect(url_for(".submit_result"))
    else:
        return redirect(url_for(".user_verify", prev=url_for(".submit_result")))

@frontend.route("/about")
def about():
    return render_template("about.html")