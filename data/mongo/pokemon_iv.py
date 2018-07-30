from data import PotClass
from .base import dict_like_mapping

class pokemon_iv_object(dict_like_mapping):
    POT_CLASS = "pot"
    VALUE = "val"
    
    @staticmethod
    def init_by_field(pot, val):
        init_dict = {
            pokemon_iv_object.POT_CLASS: pot,
            pokemon_iv_object.VALUE: val
        }

        return pokemon_iv_object(init_dict)

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @property
    def pot(self):
        return self[pokemon_iv_object.POT_CLASS]
    
    @property
    def pot_class(self):
        return PotClass.int_get_str(self.pot)

    @property
    def value(self):
        return self[pokemon_iv_object.VALUE]

    @property
    def value_class(self):
        return get_iv_class_name(self.value)
    
def get_iv_class_name(iv):
    if iv >= 0 and iv <= 33:
        return "iv-low"
    elif iv > 33 and iv <= 66:
        return "iv-medium"
    elif iv > 66 and iv <= 90:
        return "iv-high"
    elif iv > 90 and iv <= 100:
        return "iv-ex"
    else:
        return "iv-none"
