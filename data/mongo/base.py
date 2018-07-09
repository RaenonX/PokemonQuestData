from collections import MutableMapping

from pymongo.collection import Collection

class base_collection(Collection):
    def __init__(self, mongo_client, db_name, col_name, cache_keys=[]):
        super().__init__(mongo_client.get_database(db_name), col_name)
        self._cache = {}
        for k in cache_keys:
            self.init_cache(k)

    def init_cache(self, cache_key):
        self._cache[cache_key] = {}

    def set_cache(self, cache_key, item_key, item):
        if cache_key not in self._cache:
            self.init_cache(cache_key)

        self._cache[cache_key][item_key] = item

    def get_cache(self, cache_key, item_key):
        if cache_key not in self._cache:
            self.init_cache(cache_key)

        if item_key not in self._cache[cache_key]:
            self.set_cache(cache_key, item_key, self.find_one({ cache_key: item_key }))

        return self._cache[cache_key][item_key]

class dict_like_mapping(MutableMapping):
    def __init__(self, org_dict):
        if org_dict is None:
            self._dict = {}
        else:
            self._dict = dict(org_dict)

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return str(self._dict)
