from bson import ObjectId

from data import PotClass
from data.mongo import pokemon_collection, pokemon_skill_collection

from .base import base_collection, dict_like_mapping
from .pokemon_iv import pokemon_iv_object

class pokemon_manager(base_collection):
    DATABASE_NAME = "data"
    COLLECTION_NAME = "user_pokemon"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, pokemon_manager.DATABASE_NAME, pokemon_manager.COLLECTION_NAME)
        self._pkc = pokemon_collection(mongo_client)
        self._skc = pokemon_skill_collection(mongo_client)

    def insert_record(self, owner_id, pokemon_id, pokemon_name, bingo_arr, skill_arr, slot_hp, slot_atk, slot_duo, hp, atk, lv):
        poke = self._pkc.get_pokemon_by_id(pokemon_id)

        return self.insert_one(pokemon_entry.init_by_field(owner_id, pokemon_id, pokemon_name, bingo_arr, skill_arr, slot_hp, slot_atk, slot_duo, poke.get_hp_iv_obj(hp, lv), poke.get_atk_iv_obj(atk, lv), lv)).acknowledged
    
    def get_records_for_user(self, owner_id):
        """Will load pokemon data to pokemon_collection's cache"""
        ret = []
        cursor = self.find({ pokemon_entry.OWNER: owner_id })

        self._pkc.load_pokemons_to_cache(cursor.clone().distinct(pokemon_entry.POKEMON))
        self._skc.load_skills_to_cache(cursor.clone().distinct(pokemon_entry.SKILL))

        for r in cursor.clone():
            e = pokemon_entry(r, self._pkc, self._skc)
            e.poke_data = self._pkc.get_pokemon_by_id(e.pokemon_id)
            ret.append(e)
        
        return ret

    def get_record(self, id):
        result = self.find_one({ "_id": id })

        return None if result is None else pokemon_entry(result, self._pkc, self._skc)

    def edit_record(self, id, field_to_edit, value):
        return self.update_one({ "_id": id }, { "$set": { field_to_edit: value } }).acknowledged

    def delete_record(self, id):
        return self.delete_one({ "_id": ObjectId(id) }).acknowledged

class pokemon_entry(dict_like_mapping):
    OBJECT_ID = "_id"

    POKEMON = "pid"
    POKEMON_NAME = "pname"
    OWNER = "oid"
    BINGO = "bgo"
    SKILL = "skl"
    SLOTS = "slt"
    IV_PARAMS = "iv"

    @staticmethod
    def init_by_field(owner, pokemon_id, pokemon_name, bingo_arr, skill_arr, slot_hp, slot_atk, slot_duo, hp_iv_obj, atk_iv, lv):
        init_dict = {
            pokemon_entry.OWNER: owner,
            pokemon_entry.POKEMON: pokemon_id,
            pokemon_entry.POKEMON_NAME: pokemon_name,
            pokemon_entry.BINGO: bingo_arr,
            pokemon_entry.SKILL: skill_arr,
            pokemon_entry.SLOTS: slots_distribution.init_by_field(slot_hp, slot_atk, slot_duo),
            pokemon_entry.IV_PARAMS: pokemon_iv_params.init_by_field(hp_iv_obj, atk_iv, lv)
        }
        return pokemon_entry(init_dict, trans_data=False)

    def __init__(self, org_dict, pkc=None, skc=None, trans_data=True, poke_data=None):
        super().__init__(org_dict)

        if trans_data:
            _bgos = pkc.get_pokemon_by_id(self.pokemon_id).bingos
            self[pokemon_entry.BINGO] = [_bgos[i] for i in self.bingo_datas]

            self[pokemon_entry.SKILL] = [skc.get_skill_data(i) for i in self.skill_datas]
            
        self._pokedata = poke_data

    @property
    def pokemon_id(self):
        return self[pokemon_entry.POKEMON]

    @property
    def pokemon_name(self):
        return self[pokemon_entry.POKEMON_NAME]

    @property
    def owner(self):
        return self[pokemon_entry.OWNER]

    @property
    def bingo_datas(self):
        return self[pokemon_entry.BINGO]

    @property
    def skill_datas(self):
        return self[pokemon_entry.SKILL]

    @property
    def slots_dist(self):
        return slots_distribution(self[pokemon_entry.SLOTS])

    @property
    def iv_param(self):
        return pokemon_iv_params(self[pokemon_entry.IV_PARAMS])
    
    @property
    def id(self):
        return str(self[pokemon_entry.OBJECT_ID])

    @property
    def poke_data(self):
        return self._pokedata

    @poke_data.setter
    def poke_data(self, value):
        self._pokedata = value

class slots_distribution(dict_like_mapping):
    HP = "hp"
    ATK = "atk"
    DUO = "duo"

    @staticmethod
    def init_by_field(hp, atk, duo):
        init_dict = {
            slots_distribution.HP: hp,
            slots_distribution.ATK: atk,
            slots_distribution.DUO: duo
        }

        return slots_distribution(init_dict)

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @property
    def hp(self):
        return self[slots_distribution.HP]
    
    @property
    def atk(self):
        return self[slots_distribution.ATK]
    
    @property
    def duo(self):
        return self[slots_distribution.DUO]

class pokemon_iv_params(dict_like_mapping):
    HP = "hp"
    ATK = "atk"
    LV = "lv"

    @staticmethod
    def init_by_field(hp_iv_obj, atk_iv_obj, lv):
        init_dict = {
            pokemon_iv_params.HP: hp_iv_obj,
            pokemon_iv_params.ATK: atk_iv_obj,
            pokemon_iv_params.LV: lv
        }

        return slots_distribution(init_dict)

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @property
    def hp_iv_obj(self):
        return pokemon_iv_object(self[pokemon_iv_params.HP])
    
    @property
    def atk_iv_obj(self):
        return pokemon_iv_object(self[pokemon_iv_params.ATK])
    
    @property
    def lv(self):
        return self[pokemon_iv_params.LV]