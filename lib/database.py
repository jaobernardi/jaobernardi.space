import sqlite3
from time import time
from . import config
from . import utils
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from json import loads, dumps

#Setup sqlite
sqlite3.register_adapter(dict, dumps)
sqlite3.register_adapter(list, dumps)
sqlite3.register_adapter(UUID, str)
sqlite3.register_adapter(datetime, lambda x: x.timestamp())


sqlite3.register_converter('JSON', loads)
sqlite3.register_adapter('DATEANDTIME', lambda x: datetime.fromtimestamp(x))

# Tables and triggers
tables = [
    """
    CREATE TABLE IF NOT EXISTS `Salts`(
        Salt TEXT,
        UUID TEXT(36),
        PRIMARY KEY(UUID)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS `Users`(
        UUID TEXT(36),
        SaltUUID TEXT(36),
        Username TEXT,
        PasswordHash TEXT,
        Permissions JSON,
        PRIMARY KEY(UUID),
        FOREIGN KEY(SaltUUID)
            REFERENCES Salts(UUID)
            ON DELETE CASCADE        
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS `Session`(
        UserUUID TEXT,
        SessionHash TEXT,
        ValidWindow DATEANDTIME,
        FOREIGN KEY(UserUUID)
            REFERENCES Users(UUID)
            ON DELETE CASCADE
        UNIQUE(UserUUID)
    )
    """
]

triggers = [
    """
        CREATE TRIGGER IF NOT EXISTS UserSaltReverseCascadeDelete
            AFTER DELETE
                ON Users
            FOR EACH ROW
        BEGIN
            DELETE FROM Salts WHERE UUID = old.SaltUUID;
        END
    """,
]


class Database(object):
    def __enter__(self, name='default'):
        self.connection = sqlite3.connect(config.get_database_path(), detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = self.connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        return cursor
    
    def __exit__(self, *args):
        self.connection.commit()
        self.connection.close()



def setup_tables():
    with Database() as db:
        for sql in tables + triggers:
            print(sql)
            db.execute(sql)

# Salts
def create_salt(length=32):
    salt = utils.random_string(length)
    uuid = uuid4()
    with Database() as db:
        db.execute("INSERT INTO `Salts`(UUID, Salt) VALUES (?, ?)", (uuid, salt))
    return salt, uuid

#Users
def create_user(username, password, uuid=None):
    salt, salt_uuid = create_salt()
    pass_hash = utils.hash(password, salt)
    uuid = uuid or uuid4()

    with Database() as db:
        db.execute("INSERT OR REPLACE INTO `Users`(UUID, SaltUUID, Username, PasswordHash, Permissions) VALUES (?, ?, ?, ?, ?)", (uuid, salt_uuid, username, pass_hash, {}))
    return uuid, salt_uuid, username, pass_hash, {}, salt


@utils.RequireOneArg
def get_user(uuid, username, hash):
    with Database() as db:
        if hash:
            query = f"""
                SELECT
                    users.*,
                    salts.Salt
                FROM Users as users
                
                LEFT OUTER JOIN Salts as salts
                    ON salts.UUID = users.SaltUUID
                INNER JOIN Session as session
                    ON session.SessionHash = ?
                
                WHERE users.UUID = session.UserUUID
                """
            cursor = db.execute(query, (hash,))
        else:
            query = f"""
                SELECT
                    users.*,
                    salts.Salt
                FROM Users as users
                
                LEFT OUTER JOIN Salts as salts
                    ON salts.UUID = users.SaltUUID

                WHERE {'UUID = ?' if uuid else 'Username = ?'}
                """
            cursor = db.execute(query, (uuid or username,))

        data = {}
        for label, output in zip(cursor.description, cursor.fetchone()):
            data[label[0]] = output
        return data


@utils.RequireOneArg
def delete_user(uuid, username):
    with Database() as db:
        db.execute(f"DELETE FROM Users WHERE {'UUID = ?' if uuid else 'Username = ?'}", (uuid or username,))

# Sessions
def create_session(uuid):
    session = utils.random_string(64)
    session_hash = utils.hash(session)
    valid_window = datetime.now()+timedelta(hours=3)
    with Database() as db:
        db.execute("INSERT OR REPLACE INTO `Session`(UserUUID, SessionHash, ValidWindow) VALUES (?, ?, ?)", (uuid, session_hash, valid_window))
    return session_hash

def get_session(uuid):
    with Database() as db:
        cursor = db.execute("SELECT * FROM Session WHERE UserUUID = ?", (uuid,))
        data = {}
        for label, output in zip(cursor.description, cursor.fetchone()):
            data[label[0]] = output
        if data['ValidWindow'] <= time():
            db.execute("DELETE FROM Session WHERE SessionHash = ?", (data['SessionHash'],))
            return
        return data

