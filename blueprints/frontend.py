import os

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from markupsafe import escape
import pymongo

from data import RecipeQuality
from data.mongo import cook_data_manager, pokemon_collection, recipe_collection, site_log_manager

from .nav import nav

frontend = Blueprint("frontend", __name__)

mongo = pymongo.MongoClient(os.environ["MONGO_URI"])

@frontend.route("/")
def index():
    return render_template("index.html", 
                           recent=cook_data_manager(mongo).get_last_5(), 
                           site_log=site_log_manager(mongo).get_last_5())

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