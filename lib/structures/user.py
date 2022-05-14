from .. import utils
from .. import database

class User():
    def __init__(self, uuid, saltuuid, username, password_hash, permissions, salt):
        self.uuid = uuid
        self.saltuuid = saltuuid
        self.username = username
        self.password_hash = password_hash
        self.permissions = permissions
        self.salt = salt
    
    @classmethod
    def create(cls, username, password):
        db = database.create_user(username, password)
        return cls(*(db.values()))

    @property
    def session_hash(self):
        session = database.get_session(self.uuid)
        return session['SessionHash'] or None

    def create_session(self):
        database.create_session(self.uuid)

    @classmethod
    def from_username(cls, username):
        db = database.get_user(username=username)
        return cls(*(db.values()))
    
    @classmethod
    def from_session(cls, session):
        session_hash = utils.hash(session)
        db = database.get_user(hash=session_hash)
        return cls(*(db.values()))
