from data import PokeType

from .base import dict_like_mapping, base_collection

class pokemon_collection(base_collection):
    DB_NAME = "dict"
    COL_NAME = "pokemon"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, pokemon_collection.DB_NAME, pokemon_collection.COL_NAME)
        self.init_cache(pokemon.ID)

    def get_pokemon_by_id(self, id):
        return pokemon(self.get_cache(pokemon.ID, id))

    def get_pokemon_choices(self):
        ret = []

        for entry in self.find().sort([(pokemon.ID, 1)]):
            entry = pokemon(entry)
            ret.append((entry.id, "#{:03d} {}".format(entry.id, entry.name_zh)))

        return ret

class pokemon(dict_like_mapping):
    ID = "id"
    NAME_ZH = "name_zh"
    NAME_JP = "name_jp"
    NAME_EN = "name_en"
    ELEMENTS = "elem"

    def __init__(self, org_dict):
        super().__init__(org_dict)
        self[pokemon.ELEMENTS] = [PokeType(elem) for elem in self[pokemon.ELEMENTS]]
        
    @property
    def id(self):
        return self[pokemon.ID]

    @property
    def name_zh(self):
        return self[pokemon.NAME_ZH]
    
    @property
    def name_jp(self):
        return self[pokemon.NAME_JP]
    
    @property
    def name_en(self):
        return self[pokemon.NAME_EN]
    
    @property
    def elements(self):
        return self[pokemon.ELEMENTS]