import os

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from markupsafe import escape
import pymongo

from data import RecipeQuality

from .nav import nav

frontend = Blueprint("frontend", __name__)

mongo = pymongo.MongoClient(os.environ["MONGO_URI"])

@frontend.route("/")
def index():
    return render_template("index.html")

@frontend.route("/find-recipe")
def find_recipe_index():
    return render_template("poke_list.html", 
                           pokedata=mongo.dict.pokemon.find().sort([("id", pymongo.ASCENDING)]))

@frontend.route("/find-recipe/<int:id>")
def find_recipe(id):
    col = mongo.data.cook
    col2 = mongo.dict.recipe

    data_pack = []
    recipes = {}

    result = col.aggregate([
        { "$match": { "p": id } },
        { "$group": { "_id": { "r": "$r", "q": "$q" }, "count": { "$sum": 1 } } }
        ])

    for r in col.find({"p": id}).distinct("r"):
        recipes[str(r)] = col2.find({ "id": r }).next()

    for entry in result:
        recipe_comp = entry["_id"]
    
        app = entry["count"]
        app_all = col.find(recipe_comp).count()

        data_pack.append([recipe_comp["r"],
                          recipes[str(recipe_comp["r"])]["title_zh"], 
                          str(RecipeQuality(recipe_comp["q"])), 
                          app/app_all, 
                          "{} / {}".format(app, app_all),
                          recipes[str(recipe_comp["r"])]["recipe"][recipe_comp["q"]]["items"]])

    return render_template("recipe_result.html", result=sorted(data_pack, key=lambda x: x[3], reverse=True))

    
@frontend.route("/find-pokemon")
def find_pokemon_index():
    return render_template("recipe_list.html", 
                           recipedata=mongo.dict.recipe.find().sort([("id", pymongo.ASCENDING)]))

@frontend.route("/find-pokemon/<int:id>")
def find_pokemon(id):
    pass

@frontend.route("/submit-result", methods=("GET", "POST"))
def submit_result():
    pass
