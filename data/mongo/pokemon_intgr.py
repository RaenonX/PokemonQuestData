from .pokemon import pokemon

class pokemon_integrator:
    def __init__(self, pkm_col, skl_col, bgo_col):
        self._pkm_col = pkm_col
        self._skl_col = skl_col
        self._bgo_col = bgo_col

    def get_pokemon_profile(self, pokemon_id):
        return pokemon_profile(self._pkm_col.get_pokemon_by_id(pokemon_id), self._pkm_col, self._skl_col, self._bgo_col)

class pokemon_profile(pokemon):
    def __init__(self, pokemon_inst, pkm_col, skl_col, bgo_col):
        super().__init__(pokemon_inst)
        self._skills = [skl_col.get_skill_data(i) for i in self.skill_ids]
        self._skills_dlc = [skl_col.get_skill_data(i) for i in self.skill_ids_dlc]
        self._skills_unsure = [skl_col.get_skill_data(i) for i in self.skill_ids_unsure]

        _all_bingos = self.get_all_including_evolved_bingos(pkm_col)
        
        self._all_bingos = []
        for i in range(len(self.bingos)):
            self._all_bingos.append([(self.id, bgo_col.get_bingo_description(self.bingos[i]))] + [(id, bgo_col.get_bingo_description(bingos[i])) for id, bingos in _all_bingos[1:]])
        
    def get_bingos(self, index):
        """
        Parameter:
            index: 1-index.

        Return:
            [
                [(<POKEMON_ID>, <POKEMON_BINGO>), (<POKEMON_ID>, <POKEMON_BINGO>), (<POKEMON_ID>, <POKEMON_BINGO>)], 
                [(<POKEMON_ID>, <POKEMON_BINGO>), (<POKEMON_ID>, <POKEMON_BINGO>), (<POKEMON_ID>, <POKEMON_BINGO>)]
            ]
        """
        start = (index - 1) * 3
        return self._all_bingos[start: start + 3]

    @property
    def skills(self):
        return self._skills

    @property
    def skills_dlc(self):
        return self._skills_dlc

    @property
    def skills_unsure(self):
        return self._skills_unsure