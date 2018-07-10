from .pokemon import pokemon

class pokemon_integrator:
    def __init__(self, pkm_col, skl_col):
        self._pkm_col = pkm_col
        self._skl_col = skl_col

    def get_pokemon_profile(self, pokemon_id):
        return pokemon_profile(self._pkm_col.get_pokemon_by_id(pokemon_id), self._skl_col)

class pokemon_profile(pokemon):
    def __init__(self, pokemon_inst, skill_col):
        super().__init__(pokemon_inst)
        self._skills = [skill_col.get_skill_data(i) for i in self.skill_ids]

    @property
    def skills(self):
        return self._skills
