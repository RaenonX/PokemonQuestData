from bson import ObjectId
import time, json
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

    def get_cook_data_by_pokemon_id(self, id):
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

    def get_poke_data_by_recipe_id(self, id):
        _start = time.time()
        rcp = self._recipe_col.get_recipe_by_id(id)
        quality_unit_arr = []

        for x in RecipeQuality:
            filter_dict = { "r": id, "q": int(x) }

            aggr_dist_data = self.aggregate([
                { "$match": filter_dict },
                { "$group": { 
                    "_id": { 
                        "r": "$" + "r", 
                        "q": "$" + "q", 
                        "p": "$" + "p"
                    }, 
                    "count": { 
                        "$sum": 1 
                    } 
                } },
                { "$project": {
                    "_id": 0,
                    "p": "$_id.p",
                    "count": "$count"
                } },
                { "$sort": {
                    "count": -1
                } }
            ])
            total = self.find(filter_dict).count()

            quality_unit_arr.append(poke_data_quality_unit(x, rcp.get_recipe_dish(x).items, poke_data_poke_distribution(total, aggr_dist_data, self._pokemon_col)))

        return poke_data_result(rcp, quality_unit_arr, time.time() - _start)

    def get_entries_by_adder_uid(self, adder_uid, start=0, count=100):
        return [cook_data(d) for d in self._find_data_section({ cook_data.ADDER: adder_uid }, start, count)]

    def get_last(self, start=0, count=100):
        return [cook_data(d) for d in self._find_data_section({}, start, count)]

    def _find_data_section(self, query, start, count):
        return self.find(query).sort([("_id", -1)]).skip(start).limit(count)

    def get_count(self):
        return self.find().count()

    def get_adder_count(self):
        return len(self.distinct(cook_data.ADDER))

    def add_record(self, recipe_id, quality_id, pokemon_id, adder):
        return self.insert_one(cook_data.init_by_field(recipe_id, quality_id, pokemon_id, adder)).acknowledged

    def report_suspicious(self, oid_str, reporter_id):
        return self.update_one({ cook_data.OBJECT_ID: ObjectId(oid_str) }, { "$set": { cook_data.SUSPICIOUS: reporter_id } }).acknowledged

class cook_data(dict_like_mapping):
    OBJECT_ID = "_id"
    RECIPE = "r"
    QUALITY = "q"
    POKEMON_ID = "p"
    ADDER = "a"
    SUSPICIOUS = "s"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @staticmethod
    def init_by_field(recipe_id, quality_id, pokemon_id, adder):
        init_dict = {
            cook_data.RECIPE: int(recipe_id),
            cook_data.QUALITY: int(quality_id),
            cook_data.POKEMON_ID: int(pokemon_id),
            cook_data.ADDER: adder
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

    @property
    def adder_uid(self):
        return self[cook_data.ADDER]

    def get_recipe_comp_dict(self):
        return { cook_data.RECIPE: self.recipe_id, cook_data.QUALITY: int(self.quality) }

    @property
    def reportable(self):
        return cook_data.SUSPICIOUS not in self

    @property
    def suspicious(self):
        return False if cook_data.SUSPICIOUS not in self else (self[cook_data.SUSPICIOUS] != "")

    @property
    def id(self):
        return str(self[cook_data.OBJECT_ID])

##### Result Classes #####

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

class poke_data_result:
    def __init__(self, recipe, quality_unit_arr, time_consumed):
        self._recipe = recipe
        self._quality_unit_arr = quality_unit_arr
        self._time_consumed = time_consumed

    @property
    def recipe(self):
        return self._recipe

    @property
    def quality_unit_arr(self):
        return self._quality_unit_arr

    @property
    def time_consumed(self):
        return self._time_consumed

class poke_data_quality_unit:
    def __init__(self, quality, dishes, distribution):
        self._quality = quality
        self._dishes = dishes
        self._distribution = distribution

    @property
    def quality(self):
        return self._quality

    @property
    def dishes(self):
        return self._dishes

    @property
    def distribution(self):
        return self._distribution

class poke_data_poke_distribution:
    def __init__(self, total, data, pokemon_dict):
        self._total = total
        self._data = [poke_data_poke_distribution_data(total, 
                                                       dt, 
                                                       pokemon_dict.get_pokemon_by_id(dt[cook_data.POKEMON_ID]).name_zh)
                     for dt in data]

    @property
    def total(self):
        return self._total

    @property
    def data(self):
        return self._data

class poke_data_poke_distribution_data:
    def __init__(self, total, org_dict, pokename_zh):
        self._pokemon_id = org_dict[cook_data.POKEMON_ID]
        self._pokename_zh = pokename_zh
        self._count = org_dict["count"]
        self._total = total

    @property
    def pokename_zh(self):
        return self._pokename_zh

    @property
    def pokemon_id(self):
        return self._pokemon_id
    
    @property
    def count(self):
        return self._count
    
    @property
    def total(self):
        return self._total
    
    @property
    def dist_percent(self):
        return self._count / self._total
    
    def get_sample_string(self):
        return "{} / {}".format(self._count, self._total)