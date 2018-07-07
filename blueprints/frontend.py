### Use elements to get pokes
### Handle case of evolved poke
### Add statistics page

import os

from flask import (
    Blueprint, 
    render_template, flash, redirect, url_for, request, current_app
)
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from markupsafe import escape
import pymongo

from data import RecipeQuality
from data.mongo import cook_data_manager, pokemon_collection, recipe_collection, site_log_manager
from data.thirdparty import google_analytics

from .nav import nav

frontend = Blueprint("frontend", __name__)

mongo = pymongo.MongoClient(os.environ["MONGO_URI"])

@frontend.route("/")
def index():
    cdm = cook_data_manager(mongo)
    slm = site_log_manager(mongo)

    return render_template("index.html", 
                           recent=cdm.get_last(10), 
                           count=cdm.get_count(),
                           site_log=slm.get_last(7),
                           hotpages=google_analytics().get_top_unique_pageviews_by_path(),
                           site_root=current_app.config["SERVER_NAME"])

@frontend.route("/find-recipe")
def find_recipe_index():
    return render_template("poke_list.html", pokedata=mongo.dict.pokemon.find().sort([("id", pymongo.ASCENDING)]))

@frontend.route("/find-recipe/<int:id>")
def find_recipe(id):
    return render_template("recipe_result.html", result=cook_data_manager(mongo).get_cook_data_by_pokemon_id(id))
    
@frontend.route("/find-pokemon")
def find_pokemon_index():
    return render_template("recipe_list.html", recipedata=mongo.dict.recipe.find().sort([("id", pymongo.ASCENDING)]))

@frontend.route("/find-pokemon/<int:id>")
def find_pokemon(id):
    return render_template("poke_result.html", result=cook_data_manager(mongo).get_poke_data_by_recipe_id(id))

@frontend.route("/submit-result", methods=["GET"])
def submit_result():
    return render_template('submit_result.html', 
                           poke_choices=pokemon_collection(mongo).get_pokemon_choices(), 
                           recipe_choices=recipe_collection(mongo).get_recipe_choices(), 
                           quality_choices=RecipeQuality.get_choices())

@frontend.route("/submit-result", methods=["POST"])
def submit_result_post():
    acknowledged = cook_data_manager(mongo).add_record(request.form["recipe"], request.form["quality"], request.form["pokemon"])
    if acknowledged:
        flash("感謝您協助提供資料！")
        return redirect(url_for(".index"))
    else:
        flash("資料提交失敗。", category="warning")
        return redirect(url_for(".submit_result"))

@frontend.route("/about")
def about():
    return render_template("about.html")