import os

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from markupsafe import escape
import pymongo

from .forms import SignupForm
from .nav import nav

frontend = Blueprint("frontend", __name__)

mongo = pymongo.MongoClient(os.environ["MONGO_URI"])

@frontend.route("/")
def index():
    return render_template("index.html")

@frontend.route("/find-recipe")
def find_recipe_index():
    col = mongo.dict.pokemon
    return render_template("pokelist.html", pokedata=col.find().sort([("id", pymongo.ASCENDING)]))

@frontend.route("/find-recipe/<int:id>")
def find_recipe(id):
    pass

@frontend.route("/find-pokemon")
def find_pokemon_index():
    pass

@frontend.route("/submit-result", methods=("GET", "POST"))
def submit_result():
    form = SignupForm()

    if form.validate_on_submit():
        flash("Hello, {}. You have successfully signed up".format(escape(form.name.data)))

        return redirect(url_for(".index"))

    return render_template("signup.html", form=form)
