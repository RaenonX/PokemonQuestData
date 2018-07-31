### https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n
### http://jinja.pocoo.org/docs/2.10/extensions/
### https://stackoverflow.com/questions/34579316/flask-babel-how-to-translate-variables
### https://stackoverflow.com/questions/216616/how-to-create-strings-containing-double-quotes-in-excel-formulas

### https://stackoverflow.com/questions/15530487/restful-api-and-google-analytics

import os
from datetime import datetime, timedelta

from flask import (
    Blueprint,
    flash, redirect, url_for, request, current_app, session
)
from flask_mail import Message
from markupsafe import escape

from .nav import render_template
from ._objs import *

frontend = Blueprint("frontend", __name__)

@frontend.route("/")
def index():
    return render_template("index.html", 
                           recent=cdm.get_last(count=10), 
                           count=cdm.get_count(),
                           identity_count=gi.get_count(),
                           site_log=slm.get_last(7),
                           hotpages=ga.get_top_unique_pageviews_by_path(),
                           site_root=os.environ["APP_ROOT_URL"])
    
@frontend.route("/search")
def insite_search():
    q = request.args.get('q', "")
    start = int(request.args.get('start', 0))
    result_count = 20

    return render_template("insite_search.html",
                           result=gs.search(q, result_count), start=start,
                           result_limit=result_count, keyword=q)

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
                           profile=pi.get_pokemon_profile(id),
                           result=cdm.get_cook_data_by_pokemon_id(id),
                           off_prob=op.get_data_by_pokemon_id(id))

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
                           next_endpoint=".pokemon_profile_result",
                           title="從精靈查食譜",
                           mesasage="煮鍋時，只能做出第一型態的精靈。所有進化過的精靈都無法藉由煮鍋獲得。",
                           anchor="#recipe")
    
@frontend.route("/find-pokemon")
def find_pokemon_index():
    return render_template("recipe_list.html", recipedata=rcc.get_all_recipes())

@frontend.route("/find-pokemon/<int:id>")
def find_pokemon_result(id):
    return render_template("poke_result.html", 
                           result=cdm.get_poke_data_by_recipe_id(id),
                           off_prob=op.get_data_by_recipe_id(id))

@frontend.route("/about")
def about():
    return render_template("about.html")

@frontend.route("/dark-zone")
def dark_zone():
    return render_template("dz.html")

### Deprecated URLs

@frontend.route("/find-recipe/<int:id>")
def find_recipe_result(id):
    return redirect(url_for(".pokemon_profile_result", id=id) + "#recipe")