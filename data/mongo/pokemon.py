import math

from data import PokeType, SkillStone, BattleType

from .base import dict_like_mapping, base_collection

class pokemon_collection(base_collection):
    DB_NAME = "dict"
    COL_NAME = "pokemon"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, pokemon_collection.DB_NAME, pokemon_collection.COL_NAME, cache_keys=[pokemon.ID])

    def get_pokemon_by_id(self, id):
        return pokemon(self.get_cache(pokemon.ID, id))

    def get_pokemon_choices(self, including_evolved=True):
        ret = []

        for entry in self.get_all_pokemons(including_evolved):
            ret.append((entry.id, "#{:03d} {} (英: {}、日: {})".format(entry.id, entry.name_zh, entry.name_en, entry.name_jp)))

        return ret

    def get_all_pokemons(self, including_evolved=True):
        filter = {}
        if not including_evolved:
            filter[pokemon.IS_BASE_POKE] = True

        return [pokemon(entry) for entry in self.find(filter).sort([(pokemon.ID, 1)])]

    def get_count_of_pokemons(self):
        return self.find().count()

class pokemon_skill_collection(base_collection):
    DB_NAME = "dict"
    COL_NAME = "pokeskill"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, pokemon_skill_collection.DB_NAME, pokemon_skill_collection.COL_NAME, cache_keys=[poke_skill.ID])

    def get_skill_data(self, skill_id):
        return poke_skill(self.get_cache(poke_skill.ID, skill_id))

    def get_all_skills(self):
        return [poke_skill(entry) for entry in self.find().sort([(poke_skill.ID, 1)])]

class pokemon(dict_like_mapping):
    ID = "id"
    NAME_ZH = "name_zh"
    NAME_JP = "name_jp"
    NAME_EN = "name_en"
    ELEMENTS = "elem"
    EVOLVE_INFOS = "evolve_info"
    IS_BASE_POKE = "is_base"
    SKILLS = "skill"
    SKILLS_DLC = "skill_dlc"
    BATTLE_TYPE = "btl_type"

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

    @property
    def evolve_info(self):
        return self.get([poke_evolve_info(e) for e in self[EVOLVE_TO_IDS]], [])

    @property
    def is_base_pokemon(self):
        return self.get(pokemon.IS_BASE_POKE, True)

    @property
    def elements_id(self):
        return [int(e) for e in self.elements]

    @property
    def skill_ids(self):
        return self[pokemon.SKILLS]

    @property
    def skill_ids_dlc(self):
        return self[pokemon.SKILLS_DLC]

    @property
    def battle_type(self):
        return BattleType(self[pokemon.BATTLE_TYPE])

class poke_evolve_info(dict_like_mapping):
    REQ_LV = "req_lv"
    NEXT_ID = "nxt"

    def __init__(self, org_dict):
        super().__init__(org_dict)
        
    @property
    def require_lv(self):
        return self[pokemon.REQ_LV]

    @property
    def next_id(self):
        return self[pokemon.NEXT_ID]

class poke_skill(dict_like_mapping):
    ID = "id"
    ICON = "icon"
    NAME_ZH = "name_zh"
    POWER = "pwr"
    CD = "cd"
    SLOTS = "slots"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @property
    def id(self):
        return self[poke_skill.ID]

    @property
    def icon(self):
        return self[poke_skill.ICON]

    @property
    def name_zh(self):
        return self[poke_skill.NAME_ZH]

    @property
    def power(self):
        return self[poke_skill.POWER]
    
    @property
    def cd(self):
        return self[poke_skill.CD]
    
    @property
    def slots(self):
        return [SkillStone(s) for s in self[poke_skill.SLOTS]]
    
    @property
    def element(self):
        return PokeType(math.floor(self[poke_skill.ID] / 100))