from .base import dict_like_mapping, base_collection

class official_probability(base_collection):
    COLLECTION_NAME = "prob"
    DATABASE_NAME = "dict"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, official_probability.DATABASE_NAME, official_probability.COLLECTION_NAME, [probability_entry.POKEMON_ID, probability_entry.RECIPE_ID])
        self._cache_exists = {}

    def get_data_by_pokemon_id(self, poke_id):
        return probability_result(
            [probability_entry(e) for e in self.get_cache(probability_entry.POKEMON_ID, poke_id, self.find)],
            probability_entry.RECIPE_ID, probability_entry.QUALITY_ID)

    def get_data_by_recipe_id(self, recipe_id):
        return probability_result(
            [probability_entry(e) for e in self.get_cache(probability_entry.RECIPE_ID, recipe_id, self.find)],
            probability_entry.POKEMON_ID, probability_entry.QUALITY_ID)

    def data_exists(self, pokemon_id, recipe_id, quality_id):
        return self._get_cache_exists(pokemon_id, recipe_id, quality_id)

    def _get_cache_exists(self, pokemon_id, recipe_id, quality_id):
        key = "{}.{}.{}".format(pokemon_id, recipe_id, quality_id)

        if key not in self._cache_exists:
            filter = { probability_entry.POKEMON_ID: int(pokemon_id), 
                      probability_entry.RECIPE_ID: int(recipe_id), 
                      probability_entry.QUALITY_ID: int(quality_id) }
            self._cache_exists[key] = self.find_one(filter) is not None
       
        return self._cache_exists[key]

class probability_entry(dict_like_mapping):
    POKEMON_ID = "i"
    RECIPE_ID = "r"
    QUALITY_ID = "q"
    PROBABILITY = "p"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @property
    def pokemon_id(self):
        return self[probability_entry.POKEMON_ID]

    @property
    def recipe_id(self):
        return self[probability_entry.RECIPE_ID]

    @property
    def quality_id(self):
        return self[probability_entry.QUALITY_ID]

    @property
    def probability(self):
        return self[probability_entry.PROBABILITY]

class probability_result:
    def __init__(self, data, key_1, key_2):
        self._data = { "{}.{}".format(data[key_1], data[key_2]): data.probability for data in data }

    def get_data(self, key_val_1, key_val_2):
        return self._data.get("{}.{}".format(key_val_1, key_val_2))