import pymongo

class mongo_base(pymongo.collection.Collection):
    def __init__(self, database, name, create=False, codec_options=None, read_preference=None, write_concern=None, read_concern=None, session = None, **kwargs):
        super().__init__(database, name, create, codec_options, read_preference, write_concern, read_concern, session, **kwargs)
