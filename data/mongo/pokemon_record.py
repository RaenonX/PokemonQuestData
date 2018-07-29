from .base import base_collection, dict_like_mapping

class pokemon_manager(base_collection):
    DATABASE_NAME = "data"
    COLLECTION_NAME = "user_pokemon"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, pokemon_manager.DATABASE_NAME, pokemon_manager.COLLECTION_NAME)

    def insert_record(self, owner_id, pokemon_id, pokemon_name, bingo_arr, skill_arr, slot_hp, slot_atk, slot_duo, hp, atk, lv):
        return self.insert_one(pokemon_entry.init_by_field(owner_id, pokemon_id, pokemon_name, bingo_arr, skill_arr, slot_hp, slot_atk, slot_duo, hp, atk, lv)).acknowledged
    
    def get_records_of_user(self, owner_id):
        return [pokemon_entry(r) for r in self.find({ pokemon_entry.OWNER: owner_id })]

    def get_record(self, id):
        result = self.find_one({ "_id": id })

        return None if result is None else pokemon_entry(result)

    def edit_record(self, id, field_to_edit, value):
        return self.update_one({ "_id": id }, { "$set": { field_to_edit: value } }).acknowledged

    def delete_record(self, id):
        return self.delete_one({ "_id": id }).acknowledged

class pokemon_entry(dict_like_mapping):
    POKEMON = "pid"
    POKEMON_NAME = "pname"
    OWNER = "oid"
    BINGO = "bgo"
    SKILL = "skl"
    SLOTS = "slt"
    PARAMS = "prm"

    @staticmethod
    def init_by_field(owner, pokemon_id, pokemon_name, bingo_arr, skill_arr, slot_hp, slot_atk, slot_duo, hp, atk, lv):
        init_dict = {
            pokemon_entry.OWNER: owner,
            pokemon_entry.POKEMON: pokemon_id,
            pokemon_entry.POKEMON_NAME: pokemon_name,
            pokemon_entry.BINGO: bingo_arr,
            pokemon_entry.SKILL: skill_arr,
            pokemon_entry.SLOTS: slots_distribution.init_by_field(slot_hp, slot_atk, slot_duo),
            pokemon_entry.PARAMS: pokemon_params.init_by_field(hp, atk, lv)
        }
        return pokemon_entry(init_dict)

    def __init__(self, org_dict):
        super().__init__(org_dict)

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
    def bingo(self):
        return self[pokemon_entry.BINGO]

    @property
    def skill(self):
        return self[pokemon_entry.SKILL]

    @property
    def slots_dist(self):
        return slots_distribution(self[pokemon_entry.SLOTS])

    @property
    def slots_dist(self):
        return pokemon_params(self[pokemon_entry.PARAMS])

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


class pokemon_params(dict_like_mapping):
    HP = "hp"
    ATK = "atk"
    LV = "lv"

    @staticmethod
    def init_by_field(hp, atk, lv):
        init_dict = {
            pokemon_params.HP: hp,
            pokemon_params.ATK: atk,
            pokemon_params.LV: lv
        }

        return slots_distribution(init_dict)

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @property
    def hp(self):
        return self[pokemon_params.HP]
    
    @property
    def atk(self):
        return self[pokemon_params.ATK]
    
    @property
    def lv(self):
        return self[pokemon_params.LV]