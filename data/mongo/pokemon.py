import math
import json

from data import PokeType, SkillStone, BattleType, Debuff, PotClass

from .base import dict_like_mapping, base_collection
from .pokemon_iv import pokemon_iv_object

# Collection

class pokemon_collection(base_collection):
    DB_NAME = "dict"
    COL_NAME = "pokemon"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, pokemon_collection.DB_NAME, pokemon_collection.COL_NAME, cache_keys=[pokemon.ID])

    def get_pokemon_by_id(self, id):
        """Using cache."""
        return pokemon(self.get_cache(pokemon.ID, int(id)))

    def get_pokemon_choices(self, including_evolved=True):
        """Not using cache, get_all_pokemons called."""
        ret = []

        for entry in self.get_all_pokemons(including_evolved):
            ret.append((entry.id, "#{:03d} {} (英: {}、日: {})".format(entry.id, entry.name_zh, entry.name_en, entry.name_jp)))

        return ret

    def get_all_pokemons(self, including_evolved=True):
        """Not using cache."""
        filter = {}
        if not including_evolved:
            filter[pokemon.IS_BASE_POKE] = True

        return [pokemon(entry) for entry in self.find(filter).sort([(pokemon.ID, 1)])]

    def load_pokemons_to_cache(self, ids):
        """Using cache."""
        for entry in self.find({ pokemon.ID: { "$in": ids } }):
            new_poke = pokemon(entry)
            self.set_cache(pokemon.ID, new_poke.id, new_poke)

    def get_max_params_of_pokemon(self, pokemon):
        """Not using cache."""
        return PokemonParametersResult(pokemon)

    def get_count_of_pokemons(self):
        """Not using cache."""
        return self.find().count()

    def get_pokemons_by_skill_owned(self, skill_id):
        """Not using cache."""
        return [pokemon(p) for p in self.find({ pokemon.SKILLS: { "$elemMatch": { "$eq": skill_id } } }).sort([(pokemon.ID, 1)])]

class pokemon_skill_collection(base_collection):
    DB_NAME = "dict"
    COL_NAME = "pokeskill"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, pokemon_skill_collection.DB_NAME, pokemon_skill_collection.COL_NAME, cache_keys=[poke_skill.ID])

    def get_skill_data(self, skill_id):
        return poke_skill(self.get_cache(poke_skill.ID, skill_id))

    def get_all_skills(self):
        return [poke_skill(entry) for entry in self.find().sort([(poke_skill.ID, 1)])]

    def load_skills_to_cache(self, ids):
        """Using cache."""
        for entry in self.find({ poke_skill.ID: { "$in": ids } }):
            skill_data = poke_skill(entry)
            self.set_cache(pokemon.ID, skill_data.id, skill_data)

class pokemon_bingo_collection(base_collection):
    DB_NAME = "dict"
    COL_NAME = "bingo"

    SPEC_HANDLE = {
        6: [(0, PokeType.int_get_str)],
        7: [(0, PokeType.int_get_str)],
        8: [(0, PokeType.int_get_str)],
        9: [(0, Debuff.int_get_str)]
    }

    def __init__(self, mongo_client, pkm_col):
        super().__init__(mongo_client, pokemon_bingo_collection.DB_NAME, pokemon_bingo_collection.COL_NAME, cache_keys=[bingo_entry.TYPE_ID])
        self._pkm_col = pkm_col

    def get_bingo_description(self, poke_bingo):
        if poke_bingo.type_id in pokemon_bingo_collection.SPEC_HANDLE:
            for ix, trans_method in pokemon_bingo_collection.SPEC_HANDLE[poke_bingo.type_id]:
                item = poke_bingo.parameters[ix]

                # TODO: investigate why different poke_bingo but parameter is changed
                poke_bingo.parameters[ix] = item if type(item) is str else trans_method(item)

        return bingo_entry(self.get_cache(bingo_entry.TYPE_ID, poke_bingo.type_id)).get_description(poke_bingo.parameters)

# Data

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
    SKILLS_UNSURE = "skill_unsure"
    BATTLE_TYPE = "btl_type"
    BINGO = "bgo"
    BASE_VALUES = "val"
    APPEAR_RATE = "ar"
    SLOT_PCT = "slt_pct"

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
    def skill_ids_unsure(self):
        result = self[pokemon.SKILLS_UNSURE]
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
    
    @property
    def appear_rate(self):
        return self[pokemon.APPEAR_RATE]

    @property
    def slot_percentage(self):
        return poke_slot_pct(self[pokemon.SLOT_PCT])

    def get_hp_iv_obj(self, hp, lv):
        print(hp)

        if hp > 0:
            remainder = hp - self.base_values.hp - lv
            print(remainder)
            
            return self._calc_iv(remainder)
        else:
            return pokemon_iv_object.init_by_field(PotClass.UNKNOWN, -1)
        
    def get_atk_iv_obj(self, atk, lv):
        if atk > 0:
            remainder = atk - self.base_values.atk - lv

            return self._calc_iv(remainder)
        else:
            return pokemon_iv_object.init_by_field(PotClass.UNKNOWN, -1)

    def _calc_iv(self, remainder):
        checked = False
        pot = PotClass.UNKNOWN

        if remainder < 0:
            remainder = -1
            checked = True
        else:
            if not checked and remainder >= 0 and remainder <= 10:
                pot = PotClass.STEEL
                remainder *= 10
                checked = True
            
            if not checked:
                remainder -= 50
                if remainder >= 0 and remainder <= 50:
                    pot = PotClass.BRONZE
                    remainder *= 2
                    checked = True
                    
            if not checked:
                remainder -= 100
                if remainder >= 0 and remainder <= 100:
                    pot = PotClass.SILVER
                    checked = True
                    
            if not checked:
                remainder -= 150
                if remainder >= 0 and remainder <= 100:
                    pot = PotClass.GOLD
                    checked = True

        return pokemon_iv_object.init_by_field(pot, remainder if checked else -1)

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

class poke_slot_pct(dict_like_mapping):
    HP = "hp"
    ATK = "atk"
    MULTI_x1 = "m1"
    MULTI_x15 = "m15"
    MULTI_x2 = "m2"
    MULTI_x3 = "m3"

    def __init__(self, org_dict):
        super().__init__(org_dict)
        
    @property
    def hp(self):
        return self[poke_slot_pct.HP]

    @property
    def atk(self):
        return self[poke_slot_pct.ATK]

    @property
    def multi_x1(self):
        return self[poke_slot_pct.MULTI_x1]

    @property
    def multi_x15(self):
        return self[poke_slot_pct.MULTI_x15]

    @property
    def multi_x2(self):
        return self[poke_slot_pct.MULTI_x2]

    @property
    def multi_x3(self):
        return self[poke_slot_pct.MULTI_x3]

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
    
    def to_serialize(self):
        """
        [<ID>, <ELEMENT_NAME>, <NAME_ZH>]
        """

        return [self.id, str(self.element), self.name_zh]

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
    PATTERN_ZH = "pattern_zh"
    PATTERN_EN = "pattern_en"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @property
    def type_id(self):
        return self[bingo_entry.TYPE_ID]

    @property
    def pattern_zh(self):
        return self[bingo_entry.PATTERN_ZH]

    @property
    def pattern_en(self):
        return self[bingo_entry.PATTERN_EN]

    def get_description(self, params):
        return self.pattern_zh.format(*params)

# Result Classes

class PokemonParametersResult(dict_like_mapping):
    def __init__(self, pokemon):
        self._base = pokemon.base_values

    @property
    def min_atk(self):
        return self._base.atk + 1
    
    @property
    def max_atk(self):
        return self._base.atk + 501
    
    @property
    def min_hp(self):
        return self._base.hp + 1
    
    @property
    def max_hp(self):
        return self._base.hp + 501

    def toJSON(self):
        return { "min": { "atk": self.min_atk, "hp": self.min_hp }, "max": { "atk": self.max_atk, "hp": self.max_hp } }