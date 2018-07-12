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

class pokemon_bingo_collection(base_collection):
    DB_NAME = "dict"
    COL_NAME = "bingo"

    SPEC_HANDLE = {
        6: 0,
        7: 0,
        8: 0
    }

    def __init__(self, mongo_client, pkm_col):
        super().__init__(mongo_client, pokemon_bingo_collection.DB_NAME, pokemon_bingo_collection.COL_NAME, cache_keys=[bingo_entry.TYPE_ID])
        self._pkm_col = pkm_col

    def get_bingo_description(self, poke_bingo):
        if poke_bingo.type_id in pokemon_bingo_collection.SPEC_HANDLE:
            ix = pokemon_bingo_collection.SPEC_HANDLE[poke_bingo.type_id]
            poke_bingo.parameters[ix] = PokeType.int_get_str(poke_bingo.parameters[ix])

        return bingo_entry(self.get_cache(bingo_entry.TYPE_ID, poke_bingo.type_id)).get_description(poke_bingo.parameters)

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
    BINGO = "bgo"
    BASE_VALUES = "val"

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
    def evolve_infos(self):
        return [poke_evolve_info(e) for e in self[pokemon.EVOLVE_INFOS]]

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
        result = self[pokemon.SKILLS_DLC]
        return [] if result is None else result

    @property
    def battle_type(self):
        return BattleType(self[pokemon.BATTLE_TYPE])

    @property
    def base_values(self):
        return poke_base_val(self[pokemon.BASE_VALUES])

    @property
    def bingos(self):
        return [poke_bingo(b) for b in self[pokemon.BINGO]]

    def get_all_including_evolved_bingos(self, pkm_col):
        """
        Return:
            [(<POKEMON_ID>, <POKEMON_BINGOS>), (<POKEMON_ID>, <POKEMON_BINGOS>)...]
        """
        ret = [(self.id, self.bingos)]

        for evolve_info in self.evolve_infos:
            ret.extend(pkm_col.get_pokemon_by_id(evolve_info.next_id).get_all_including_evolved_bingos(pkm_col))

        return ret

class poke_evolve_info(dict_like_mapping):
    REQ_LV = "req_lv"
    NEXT_ID = "nxt"

    def __init__(self, org_dict):
        super().__init__(org_dict)
        
    @property
    def require_lv(self):
        return self[poke_evolve_info.REQ_LV]

    @property
    def next_id(self):
        return self[poke_evolve_info.NEXT_ID]

class poke_skill(dict_like_mapping):
    ID = "id"
    ICON = "icon"
    NAME_ZH = "name_zh"
    POWER = "pwr"
    CD = "cd"
    SLOTS = "slots"
    DESCRIPTION = "desc"

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
    def description(self):
        return self.get(poke_skill.DESCRIPTION, "(無資料)")
    
    @property
    def element(self):
        return PokeType(math.floor(self[poke_skill.ID] / 100))

class poke_bingo(dict_like_mapping):
    TYPE_ID = "type"
    PARAMETER = "param"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @property
    def type_id(self):
        return self[poke_bingo.TYPE_ID]

    @property
    def parameters(self):
        return self[poke_bingo.PARAMETER]

class poke_base_val(dict_like_mapping):
    HP = "hp"
    ATK = "atk"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @property
    def hp(self):
        return self[poke_base_val.HP]

    @property
    def atk(self):
        return self[poke_base_val.ATK]

class bingo_entry(dict_like_mapping):
    TYPE_ID = "id"
    PATTERN = "pattern"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @property
    def type_id(self):
        return self[bingo_entry.TYPE_ID]

    @property
    def pattern(self):
        return self[bingo_entry.PATTERN]

    def get_description(self, params):
        print(params)
        print(self.pattern)
        print(self.pattern.format(*params))
        print("")
        return self.pattern.format(*params)