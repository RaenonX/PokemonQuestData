from .base import dict_like_mapping, base_collection

class official_probability(base_collection):
    COLLECTION_NAME = "prob"
    DATABASE_NAME = "dict"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, official_probability.DATABASE_NAME, official_probability.COLLECTION_NAME, [probability_entry.POKEMON_ID])

    def get_data_by_pokemon_id(self, poke_id):
        return probability_result([probability_entry(e) for e in self.get_cache(probability_entry.POKEMON_ID, poke_id, self.find)])

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
    def __init__(self, data):
        self._data = { "{}.{}".format(data.recipe_id, data.quality_id): data.probability for data in data }

    def get_data(self, recipe_id, quality_id):
        return self._data.get("{}.{}".format(recipe_id, quality_id))