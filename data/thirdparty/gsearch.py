import os
import json
import requests

from data.mongo.base import dict_like_mapping

class google_search:
    API_URL = "https://www.googleapis.com/customsearch/v1/siterestrict"
    SINGLE_QUERY_LIMIT = 10

    def __init__(self):
        self._api_key = os.environ.get("GS_KEY")
        self._cx = os.environ.get("GS_CX")
        self._disabled = False

        if self._api_key is None:
            print("Specify 'GS_API_KEY' (Google Custom Search API Key), or google_search will be disabled.")
            self._disabled = True

        if self._api_key is None:
            print("Specify 'GS_CX' (Google Custom Search Engine ID), or google_search will be disabled.")
            self._disabled = True
            
    def search(self, query, count=None, start=None):
        ret = []

        if self._disabled:
            print("google_search is disabled.")
            return ret

        params = { "key": self._api_key, "cx": self._cx, "q": query }

        if count is not None:
            params["num"] = count

        if start is not None:
            params["start"] = start

        arr = self._generate_num_arr(count, start)

        for st, num in arr:
            params["num"] = num
            params["start"] = st
            response = requests.get(google_search.API_URL, params=params)
            response = json.loads(response.text)

            if "items" in response:
                for i in response["items"]:
                    ret.append(search_result_object(i))

        return ret

    def _generate_num_arr(self, count, start):
        ret = []
        
        if start is None:
            start = 1

        if count is None:
            ret.append((start, 
                        google_search.SINGLE_QUERY_LIMIT if count is None else google_search.SINGLE_QUERY_LIMIT if count % google_search.SINGLE_QUERY_LIMIT == 0 else count % google_search.SINGLE_QUERY_LIMIT))
        else:
            last_i = count // google_search.SINGLE_QUERY_LIMIT - 1

            for i in range(count // google_search.SINGLE_QUERY_LIMIT):
                ret.append((i * google_search.SINGLE_QUERY_LIMIT + 1, (google_search.SINGLE_QUERY_LIMIT if count % google_search.SINGLE_QUERY_LIMIT == 0 else count % google_search.SINGLE_QUERY_LIMIT) if i == last_i else google_search.SINGLE_QUERY_LIMIT))

        return ret

class search_result_object(dict_like_mapping):
    TITLE = "title"
    HTML_TITLE = "html_title"
    LINK = "link"
    SNIPPET = "snippet"

    def __init__(self, org_dict):
        super().__init__(org_dict)
        
    @property
    def title(self):
        return self[search_result_object.TITLE]

    @property
    def html_title(self):
        return self[search_result_object.HTML_TITLE]
    
    @property
    def link(self):
        return self[search_result_object.LINK]
    
    @property
    def snippet(self):
        return self[search_result_object.SNIPPET]