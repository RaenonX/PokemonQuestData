from .base import dict_like_mapping, base_collection

class recipe_collection(base_collection):
    DB_NAME = "dict"
    COL_NAME = "recipe"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, recipe_collection.DB_NAME, recipe_collection.COL_NAME, cache_keys=[recipe.ID])

    def get_recipe_choices(self):
        ret = []

        for entry in self.find().sort([(recipe.ID, 1)]):
            entry = recipe(entry)
            ret.append((entry.id, "{} ({}；{}愛吃的東西)".format(entry.title_zh, entry.description_zh, entry.result_zh)))

        return ret

    def get_recipe_by_id(self, id):
        return recipe(self.get_cache(recipe.ID, id))

class recipe(dict_like_mapping):
    ID = "id"
    TITLE_ZH = "title_zh"
    DESCRIPTION_ZH = "description_zh"
    RESULT_ZH = "result_zh"

    RECIPE = "recipe"

    def __init__(self, recipe_dict):
        super().__init__(recipe_dict)
        self[recipe.RECIPE] = [recipe_dish(rcp) for rcp in self[recipe.RECIPE]]

    @property
    def id(self):
        return self[recipe.ID]

    @property
    def title_zh(self):
        return self[recipe.TITLE_ZH]

    @property
    def description_zh(self):
        return self[recipe.DESCRIPTION_ZH]

    @property
    def result_zh(self):
        return self[recipe.RESULT_ZH]
    
    def get_recipe_dish(self, quality):
        return recipe_dish(self[recipe.RECIPE][int(quality)])

class recipe_dish(dict_like_mapping):
    TIME = "time"
    ITEMS = "items"

    def __init__(self, recipe_dict):
        super().__init__(recipe_dict)

    @property
    def time(self):
        return self[recipe_dish.TIME]

    @property
    def items(self):
        return [] if recipe_dish.ITEMS not in self else self[recipe_dish.ITEMS]