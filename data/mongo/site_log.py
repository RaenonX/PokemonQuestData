from datetime import datetime

from ex import EnumWithName

from .base import base_collection, dict_like_mapping

class site_log_manager(base_collection):
    DB_NAME = "data"
    COL_NAME = "site_log"

    def __init__(self, mongo_client):
        super().__init__(mongo_client, site_log_manager.DB_NAME, site_log_manager.COL_NAME)

    def insert_record(self, type, content, timestamp=datetime.today()):
        return self.insert_one(site_log_entry.init_by_field(type, content, timestamp)).acknowledged

    def get_last_5(self):
        return [site_log_entry(d) for d in self.find().sort([("_id", -1)]).limit(5)]

class site_log_entry(dict_like_mapping):
    TYPE = "tp"
    CONTENT = "c"
    TIMESTAMP = "t"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @staticmethod
    def init_by_field(type, content, timestamp):
        init_dict = {
            site_log_entry.TYPE: type,
            site_log_entry.CONTENT: content,
            site_log_entry.TIMESTAMP: timestamp
        }

        return site_log_entry(init_dict)

    @property
    def timestamp(self):
        return self[site_log_entry.TIMESTAMP]

    @property
    def content(self):
        return self[site_log_entry.CONTENT]

    @property
    def type(self):
        return log_type(self[site_log_entry.TYPE])

class log_type(EnumWithName):
    INFO = 0, 'info'
    SUCCESS = 1, 'success'
    WARNING = 2, 'warning'
    DANGER = 3, 'danger'
