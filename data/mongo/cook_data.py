import time
from datetime import datetime

from data import RecipeQuality

from .base import base_collection, dict_like_mapping
from .pokemon import pokemon_collection
from .recipe import recipe_collection

class cook_data_manager(base_collection):
    DB_NAME = "data"
    COL_NAME = "cook"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, cook_data_manager.DB_NAME, cook_data_manager.COL_NAME)
        self._pokemon_col = pokemon_collection(mongo_client)
        self._recipe_col = recipe_collection(mongo_client)

    def get_data_collection_by_pokemon_id(self, id):
        _start = time.time()

        data_pack = []

        filter_dict = { cook_data.POKEMON_ID: id }

        result = self.aggregate([
            { "$match": filter_dict },
            { "$group": { 
                "_id": { 
                    cook_data.RECIPE: "$" + cook_data.RECIPE, 
                    cook_data.QUALITY: "$" + cook_data.QUALITY, 
                    cook_data.POKEMON_ID: "$" + cook_data.POKEMON_ID 
                }, 
                "count": { 
                    "$sum": 1 
                } 
            } 
        }])

        for entry in result:
            entry_cook_data = cook_data(entry["_id"])

            data_pack.append(cook_data_result(self._recipe_col.get_recipe_by_id(entry_cook_data.recipe_id), 
                                              entry_cook_data.quality,
                                              entry["count"],
                                              self.find(entry_cook_data.get_recipe_comp_dict()).count()))

        return cook_data_result_collection(self._pokemon_col.get_pokemon_by_id(id),
                                           sorted(data_pack, key=lambda x: x.probability, reverse=True), 
                                           time.time() - _start)

    def get_last_5(self):
        return [cook_data(d) for d in self.find().sort([("_id", -1)]).limit(5)]

    def add_record(self, recipe_id, quality_id, pokemon_id):
        return self.insert_one(cook_data.init_by_field(recipe_id, quality_id, pokemon_id)).acknowledged

class cook_data(dict_like_mapping):
    RECIPE = "r"
    QUALITY = "q"
    POKEMON_ID = "p"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @staticmethod
    def init_by_field(recipe_id, quality_id, pokemon_id):
        init_dict = {
            cook_data.RECIPE: int(recipe_id),
            cook_data.QUALITY: int(quality_id),
            cook_data.POKEMON_ID: int(pokemon_id)
        }
        return cook_data(init_dict)

    @property
    def timestamp(self):
        return datetime.fromordinal(1) if "_id" not in self else self["_id"].generation_time

    @property
    def recipe_id(self):
        return self[cook_data.RECIPE]

    @property
    def quality(self):
        return RecipeQuality(self[cook_data.QUALITY])

    @property
    def pokemon_id(self):
        return self[cook_data.POKEMON_ID]

    def get_recipe_comp_dict(self):
        return { cook_data.RECIPE: self.recipe_id, cook_data.QUALITY: int(self.quality) }

class cook_data_result:
    def __init__(self, recipe, recipe_quality, appearance, appearance_all):
        self._recipe = recipe
        self._recipe_quality = recipe_quality
        self._appearance = appearance
        self._appearance_all = appearance_all
        
    @property
    def recipe(self):
        return self._recipe

    @property
    def recipe_quality(self):
        return self._recipe_quality

    @property
    def recipe_dish(self):
        return self._recipe.get_recipe_dish(self._recipe_quality)

    @property
    def probability(self):
        return self._appearance / self._appearance_all

    @property
    def appearance(self):
        return self._appearance

    @property
    def sample_count(self):
        return self._appearance_all

    @property
    def processing_time(self):
        return self._proc_time

    def get_sample_size_string(self):
        return "{} / {}".format(self._appearance, self._appearance_all)

class cook_data_result_collection:
    def __init__(self, pokemon, data_collection, time_consumed):
        self._pokemon = pokemon
        self._data_collection = data_collection
        self._time_consumed = time_consumed

    @property
    def pokemon(self):
        return self._pokemon

    @property
    def data(self):
        return self._data_collection

    @property
    def time_consumed(self):
        return self._time_consumed