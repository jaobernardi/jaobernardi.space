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

