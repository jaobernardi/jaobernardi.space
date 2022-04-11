from base64 import b64encode
import sqlite3

from . import config, utils
from hashlib import sha512, sha256
from uuid import uuid4

tables = [
    """
        CREATE TABLE `Salts`(
            UUID TEXT(36),
            Salt TEXT(128),
            PRIMARY KEY(UUID)
        )
    """,
    """
        CREATE TABLE `Users`(
            UUID TEXT(36),
            Username TEXT,
            PasswordHash LONGTEXT,
            SaltUUID TEXT(36),
            HttpAuthHash LONGTEXT,
            PRIMARY KEY(UUID),
            FOREIGN KEY(SaltUUID) 
                REFERENCES Salts(UUID)
                ON DELETE CASCADE
        )
    """,
    """
        CREATE TABLE `Sessions`(
            UserUUID TEXT(36),
            SessionHash LONGTEXT,
            IPIssuerHash LONGTEXT,
            SaltUUID TEXT(36),
            TTL DATETIME,
            PRIMARY KEY(SessionHash),
            FOREIGN KEY(UserUUID) 
                REFERENCES Users(UUID)
                ON DELETE CASCADE,
            FOREIGN KEY(SaltUUID) 
                REFERENCES Salts(UUID)
                ON DELETE CASCADE
        )
    """,
    """
        CREATE TABLE `Tokens`(
            TokenHash LONGTEXT,
            UserUUID TEXT(36),
            TTL DATETIME,
            PRIMARY KEY(TokenHash),
            FOREIGN KEY(UserUUID)
                REFERENCES Users(UUID)
                ON DELETE CASCADE
            
        )
    """,
    """
        CREATE TABLE `Spotify`(
            UserUUID TEXT(36),
            ClientID TEXT,
            RefreshToken TEXT(128),
            ExpireToken DATETIME,
            AccessToken TEXT(128),
            PRIMARY KEY(ClientID),
            FOREIGN KEY(UserUUID)
                REFERENCES Users(UUID)
                ON DELETE CASCADE
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
    """
        CREATE TRIGGER IF NOT EXISTS SessionSaltReverseCascadeDelete
            AFTER DELETE
                ON Sessions
            FOR EACH ROW
        BEGIN
            DELETE FROM Salts WHERE UUID = old.SaltUUID;
        END
    """
]

class DatabaseConnection(object):
    def __enter__(self, name='default'):
        self.connection = sqlite3.connect(config.get_database()['default'])
        cursor = self.connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        return cursor
    
    def __exit__(self, *args):
        self.connection.commit()
        self.connection.close()



def setup_tables():
    with DatabaseConnection() as db:
        for sql in tables + triggers:
            print(sql)
            db.execute(sql)

# Salt methods
# Create salt
def create_salt(length=32):
    salt = utils.random_string(length)
    uuid = uuid4()
    with DatabaseConnection() as db:
        db.execute("INSERT INTO `Salts`(UUID, Salt) VALUES (?, ?)", (str(uuid), salt))
    return salt, uuid

# Get an individual salt
def get_salt(uuid):
    with DatabaseConnection() as db:
        cursor = db.execute("SELECT Salt FROM Salts WHERE UUID = ?", (uuid,))
        return [i for i in cursor][0]

# Get all salts
def get_salts():
    with DatabaseConnection() as db:
        cursor = db.execute("SELECT Salt FROM Salts WHERE 1=1")
        return [i for i in cursor]

# Delete a salt
def delete_salt(uuid):
    """Warning: Deleting a salt will cascade delete all inserts related to it."""
    with DatabaseConnection() as db:
        cursor = db.execute("DELETE FROM Salts WHERE UUID = ?", (uuid,))

# User methods
# Add user
def add_user(username, password):
    salt, salt_uuid = create_salt()
    password_hash = sha256()
    password_hash.update(password.encode('utf-8'))
    password_hash.update(salt.encode('utf-8'))
    password_hash = password_hash.hexdigest()
    http_auth = sha256(b64encode(f'{username}:{password}{salt}'.encode())).hexdigest()
    uuid = uuid4()

    with DatabaseConnection() as db:
        db.execute("INSERT INTO `Users`(UUID, Username, PasswordHash, SaltUUID, HttpAuthHash) VALUES (?, ?, ?, ?, ?)", (str(uuid), username, password_hash, str(salt_uuid), http_auth))
    return uuid, salt_uuid

# Get all users
def get_users():
    with DatabaseConnection() as db:
        query = """
            SELECT
                u.*,
                stus.Salt,
                t.TokenHash,
                t.TTL,
                ss.SessionHash,
                ss.IPIssuerHash,
                ss.SaltUUID,
                ss.TTL,
                stss.Salt,
                sp.ClientID,
                sp.RefreshToken,
                sp.ExpireToken
            FROM Users as u
            LEFT OUTER JOIN Tokens as t
                ON t.UserUUID = u.UUID
            LEFT OUTER JOIN Sessions as ss
                ON ss.UserUUID = u.UUID
            LEFT OUTER JOIN Spotify as sp
                ON sp.UserUUID = u.UUID
            LEFT OUTER JOIN Salts as stus
                ON stus.UUID = u.SaltUUID
            LEFT OUTER JOIN Salts as stss
                ON stss.UUID = ss.SaltUUID
            WHERE 1=1
            """
        cursor = db.execute(query)
        users = []
        # Loop users in query
        for data in cursor:
            # Create a dict for user data
            users.append(utils.DuplicateKeyDict())
            # Loop data in user and its labels
            for label, data in zip(cursor.description, data):
                users[-1][label[0]] = data
        return users

# Get a specific user
@utils.RequireOneArg
def get_user(username, uuid):
    with DatabaseConnection() as db:
        query = """
            SELECT
                u.*,
                stus.Salt,
                t.TokenHash,
                t.TTL,
                ss.SessionHash,
                ss.IPIssuerHash,
                ss.SaltUUID,
                ss.TTL,
                stss.Salt,
                sp.ClientID,
                sp.RefreshToken,
                sp.ExpireToken
            FROM Users as u
            LEFT OUTER JOIN Tokens as t
                ON t.UserUUID = u.UUID
            LEFT OUTER JOIN Sessions as ss
                ON ss.UserUUID = u.UUID
            LEFT OUTER JOIN Spotify as sp
                ON sp.UserUUID = u.UUID
            LEFT OUTER JOIN Salts as stus
                ON stus.UUID = u.SaltUUID
            LEFT OUTER JOIN Salts as stss
                ON stss.UUID = ss.SaltUUID
            WHERE
            """  + f"u.Username = ?" if username else f'u.UUID = ?'
        cursor = db.execute(query, (username or uuid,))
        user = utils.DuplicateKeyDict()
        data = [i for i in cursor][0]
        for label, data in zip(cursor.description, data):
            user[label[0]] = data
        return user

def get_user_by_token(token_hash):
    with DatabaseConnection() as db:
        cursor = db.execute("""
            SELECT
                UserUUID
            FROM Tokens
            WHERE TokenHash = ?
        """, (token_hash,))
        user_uuid = [i for i in cursor][0]
    return get_user(uuid=user_uuid)

def get_user_by_session(session_hash):
    with DatabaseConnection() as db:
        cursor = db.execute("""
            SELECT
                UserUUID
            FROM Sessions
            WHERE SessionHash = ?
        """, (session_hash,))
        user_uuid = [i for i in cursor][0]
    return get_user(uuid=user_uuid)

def get_user_by_spotify(client_id):
    with DatabaseConnection() as db:
        cursor = db.execute("""
            SELECT
                UserUUID
            FROM Spotify
            WHERE ClientID = ?
        """, (client_id,))
        user_uuid = [i for i in cursor][0]
    return get_user(uuid=user_uuid)

# Delete an user.
@utils.RequireOneArg
def delete_user(username, uuid):
    with DatabaseConnection() as db:
        db.execute("""
            DELETE FROM Users
            WHERE
        """ + f"Username = ?" if username else f'UUID = ?', (username or uuid,))

# Session methods
def create_session(ipissuer, ttl, user_uuid=None):
    salt, salt_uuid = create_salt()
    session_token = utils.random_string(64)
    session_hash = session_token+salt
    session_hash = sha256(session_hash.encode()).hexdigest()
