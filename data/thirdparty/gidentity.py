import os
from datetime import datetime

from data.mongo.base import base_collection, dict_like_mapping
from ex import EnumWithName

from google.oauth2 import id_token
from google.auth.transport import requests

class google_identity(base_collection):
    DATABASE_NAME = "validation"
    COLLECTION_NAME = "google"

    def __init__(self, mongo_client):
        self._disabled = False

        self._client_id = os.environ.get("GI_CLIENT_ID")

        if self._client_id is None:
            print("Specify 'GI_CLIENT_ID' as google identity api client id in the environments variable, or this class will be disabled.")
            self._disabled = True

        super().__init__(mongo_client, google_identity.DATABASE_NAME, google_identity.COLLECTION_NAME)

    def user_exists(self, session):
        if g_user_instance.ID not in session:
            return False

        exists = self.find({ g_user_instance.ID: session[g_user_instance.ID] }).count() > 0
        if not exists:
            del session[g_user_instance.ID]
            return False 
        
        return True

    def register_user(self, email, token, session):
        """
        Return:
            The result of registering a user.
        """
        if self._disabled:
            print("class <google_identity> has been disabled.")
            return False

        uid = self.get_user_id_from_token(token)

        self.find_one_and_update({ g_user_instance.ID: uid }, g_user_instance.new_dict_for_update(email, uid), upsert=True)
        session[g_user_instance.ID] = uid

        return True

    def get_user_id_from_token(self, token):
        """
        Return:
            None if the token is invalid.
        """
        if self._disabled:
            print("class <google_identity> has been disabled.")
            return False

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), self._client_id)
        
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
        
            return idinfo['sub']
        except ValueError:
            return None

class g_user_instance(dict_like_mapping):
    EMAIL = "email"
    ID = "uid"
    BLOCKED = "blocked"
    SUPPRESS_TILL = "supress_till"

    def __init__(self, org_dict):
        super().__init__(org_dict)

    @staticmethod
    def new_dict_for_update(email, uid):
        d = { "$set": {
            g_user_instance.EMAIL: email,
            g_user_instance.ID: uid,
            g_user_instance.BLOCKED: False,
            g_user_instance.SUPPRESS_TILL: None
        } }

        return d

    @property
    def email(self):
        return self[g_user_instance.EMAIL]
    
    @property
    def uid(self):
        return self[g_user_instance.ID]
    
    @property
    def blocked(self):
        return self[g_user_instance.BLOCKED]
    
    @property
    def supress_end_timestamp(self):
        return self[g_user_instance.SUPPRESS_TILL]

    @property
    def status(self):
        if self.blocked:
            return user_status.BLOCKED

        if self.supress_end_timestamp is not None and self.supress_end_timestamp > datetime.utcnow():
            return user_status.SUPPRESSED

        return user_status.AVAILABLE

class user_status(EnumWithName):
    NOT_REGISTERED = 0, "未註冊"
    AVAILABLE = 1, "一般"
    SUPPRESSED = 2, "停權"
    BLOCKED = 3, "封鎖"