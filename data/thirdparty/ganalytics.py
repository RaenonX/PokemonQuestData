import os
import json
from datetime import datetime

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

class google_analytics:
    # KEY 1: Metric: Unique Page View | Dimension: ["Page Path", "Page Title"] | Sort: Unique Page View DESCENDING

    SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
    DATA_KEY_1 = "UNIQUE_PGV_BY_PATH"

    UPDATE_FREQ_SECS = 60

    def __init__(self):
        self._disabled = False
        self._data = google_analytics_cache([google_analytics.DATA_KEY_1])
        self._init_credential()
        self._init_data()

    def _init_credential(self):
        credential = os.environ.get("GA_JSON")
        if credential is None:
            print("Specify 'GA_JSON' as Google API client credential in environment variables, or this class will be disabled.")
            self._disabled = True

        self._view_id = os.environ.get("GA_VIEW_ID")
        if self._view_id is None:
            print("Specify 'GA_VIEW_ID' as Google API client credential in environment variables, or this class will be disabled.")
            self._disabled = True

        if not self._disabled:
            credential = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(credential), google_analytics.SCOPES)

            self._analytics = build('analyticsreporting', 'v4', credentials=credential)

    def _init_data(self):
        self._cache_1()

    def _cache_1(self):
        if not self._disabled:
            response = self._get_report({
                'reportRequests': [{
                    'viewId': self._view_id,
                    'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
                    'metrics': [{'expression': 'ga:uniquePageviews'}],
                    'dimensions': [{'name': 'ga:pagePath'}, {'name': 'ga:pageTitle'}],
                    "pageSize": 10,
                    "orderBys": [{
                        "fieldName": "ga:uniquePageviews",
                        "sortOrder": "DESCENDING"
                    }],
                    "dimensionFilterClauses": [{
                        "operator": "AND",
                        "filters": [
                            {
                                "dimensionName": "ga:pageTitle",
                                "not": True,
                                "expressions": ["Pokemon Quest 資料站"],
                                "operator": "EXACT"
                            },
                            {
                                "dimensionName": "ga:pagePath",
                                "not": True,
                                "expressions": ["/", "/prevent-sleep"],
                                "operator": "EXACT"
                            }
                        ]
                    }]
                }]
            })

            try:
                self._data.set_data(google_analytics.DATA_KEY_1, [
                    (entry["dimensions"][0],
                     entry["dimensions"][1],
                     int(entry["metrics"][0]["values"][0])) for entry in response["reports"][0]["data"]["rows"]])
            except Exception as e:
                print(e)
                print(json.dumps(response, indent=4, sort_keys=True))
                self._data.set_data(google_analytics.DATA_KEY_1)
                return
        else:
            self._data.set_data(google_analytics.DATA_KEY_1, [])

    def _get_report(self, report_requests):
        if not self._disabled:
            return self._analytics.reports().batchGet(body=report_requests).execute()

    def get_top_unique_pageviews_by_path(self, limit=10):
        """
        Returns:
            [(<PATH>, <PAGE_TITLE>, <UNIQUE_PAGEVIEWS>), (<PATH>, <PAGE_TITLE>, <UNIQUE_PAGEVIEWS>), (<PATH>, <PAGE_TITLE>, <UNIQUE_PAGEVIEWS>)...]
        """
        if not self._disabled:
            data = self._data.get_data(google_analytics.DATA_KEY_1)

            if (datetime.utcnow() - data.updated_time).total_seconds() > google_analytics.UPDATE_FREQ_SECS or data.data is None:
                self._cache_1()

            return self._data.get_data(google_analytics.DATA_KEY_1)
        else:
            return []

class google_analytics_cache:
    def __init__(self, init_field_keys=[]):
        self._data = {}
        for i in init_field_keys:
            self.set_data(i)

    def set_data(self, key, dt=None):
        if dt is None:
            self._data[key] = google_analytics_cache_item() 
        else:
            self._data[key].data = dt

    def get_data(self, key):
        if key not in self._data:
            self.set_data(key)

        return self._data[key]

class google_analytics_cache_item:
    def __init__(self):
        self.data = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, dt):
        self._updated_time = datetime.utcnow()
        self._data = dt

    @property
    def updated_time(self):
        return self._updated_time