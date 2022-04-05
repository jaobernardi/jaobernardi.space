import sqlite3
from . import config

tables = [
    """
        CREATE TABLE `Users`(
            UUID TEXT(36),
            Username TEXT,
            Password LONGTEXT,
            HttpAuth LONGTEXT,
            PRIMARY KEY UUID,
        )
    """,
    """
        CREATE TABLE `spotify_auth`(
            UserUUID TEXT(36),
            ClientID TEXT,
            RefreshToken TEXT(128),
            ExpireToken DATETIME,
            AccessToken TEXT(128),
            PRIMARY KEY ClientID,
            FOREIGN KEY(UserUUID) REFERENCES Users(UUID)
        )
    """,
]

class DatabaseConnection(object):
    def __enter__(self, name='default'):
        self.connection = sqlite3.connect(config.get_database()['default'])
        return self.connection.cursor()
    
    def __exit__(self, *args):
        self.connection.commit()
        self.connection.close()


def setup_tables():
    with DatabaseConnection() as db:
        for sql in tables:
            db.execute(sql)


def add_user(username, password):
    """
    add_user(user_id, password)
    -----

    """