import os
import pymongo

from data import RecipeQuality, PokeType
from data.mongo import (
    cook_data_manager,
    pokemon_collection, pokemon_skill_collection, pokemon_bingo_collection, recipe_collection, 
    site_log_manager, pokemon_integrator, pokemon_manager,
    official_probability
)
from data.thirdparty import (
    google_analytics, google_identity, google_recaptcha, google_search,
    identity_entry_uid_key
)

mongo = pymongo.MongoClient(os.environ["MONGO_URI"])

cdm = cook_data_manager(mongo)

pkc = pokemon_collection(mongo)
rcc = recipe_collection(mongo)
skc = pokemon_skill_collection(mongo)
bgc = pokemon_bingo_collection(mongo, pkc)

pi = pokemon_integrator(pkc, skc, bgc)
pm = pokemon_manager(mongo)

op = official_probability(mongo)

slm = site_log_manager(mongo)
ga = google_analytics()
gi = google_identity(mongo)
gr = google_recaptcha()
gs = google_search()
