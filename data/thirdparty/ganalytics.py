import os
import json

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

class google_analytics:
    SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
    VIEW_ID = '178107086'

    def __init__(self):
        self._disabled = False
        self._init_credential()

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

    def _get_report(self, report_requests):
        if not self._disabled:
            return self._analytics.reports().batchGet(body=report_requests).execute()

    def get_top_unique_pageviews_by_path(self, limit=10):
        """
        Returns:
            [(<PATH>, <UNIQUE_PAGEVIEWS>), (<PATH>, <UNIQUE_PAGEVIEWS>), (<PATH>, <UNIQUE_PAGEVIEWS>)...]
            Return none if error occurred when acquiring data or the object is disabled.
        """
        if not self._disabled:
            response = self._get_report({
                'reportRequests': [{
                    'viewId': self._view_id,
                    'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
                    'metrics': [{'expression': 'ga:uniquePageviews'}],
                    'dimensions': [{'name': 'ga:pagePath'}],
                    "pageSize": limit,
                    "orderBys": [{
                        "fieldName": "ga:uniquePageviews",
                        "sortOrder": "DESCENDING"
                    }]
                }]
            })

            try:
                return [(entry["dimensions"][0], int(entry["metrics"][0]["values"][0])) for entry in response["reports"][0]["data"]["rows"]]
            except Exception as e:
                print(e)
                return []
        else:
            return []