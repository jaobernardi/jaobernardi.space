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
            TTL DATETIME,
            PRIMARY KEY(SessionHash),
            FOREIGN KEY(UserUUID) 
                REFERENCES Users(UUID)
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
        CREATE TRIGGER IF NOT EXISTS TTLChecker
            BEFORE 
    """
]  

class Database(object):
    def __enter__(self, name='default'):
        self.connection = sqlite3.connect(config.get_database()['default'])
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

# Salt methods
# Create salt
def create_salt(length=32):
    salt = utils.random_string(length)
    uuid = uuid4()
    with Database() as db:
        db.execute("INSERT INTO `Salts`(UUID, Salt) VALUES (?, ?)", (str(uuid), salt))
    return salt, uuid

# Get an individual salt
def get_salt(uuid):
    with Database() as db:
        cursor = db.execute("SELECT Salt FROM Salts WHERE UUID = ?", (uuid,))
        return [i for i in cursor][0]

# Get all salts
def get_salts():
    with Database() as db:
        cursor = db.execute("SELECT Salt FROM Salts WHERE 1=1")
        return [i for i in cursor]

# Delete a salt
def delete_salt(uuid):
    """Warning: Deleting a salt will cascade delete all inserts related to it."""
    with Database() as db:
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

    with Database() as db:
        db.execute("INSERT INTO `Users`(UUID, Username, PasswordHash, SaltUUID, HttpAuthHash) VALUES (?, ?, ?, ?, ?)", (str(uuid), username, password_hash, str(salt_uuid), http_auth))
    return uuid, salt_uuid

# Get all users
def get_users():
    with Database() as db:
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
    with Database() as db:
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
    with Database() as db:
        cursor = db.execute("""
            SELECT
                UserUUID
            FROM Tokens
            WHERE TokenHash = ?
        """, (token_hash,))
        user_uuid = [i for i in cursor][0]
    return get_user(uuid=user_uuid)

def get_user_by_session(session_hash):
    with Database() as db:
        cursor = db.execute("""
            SELECT
                UserUUID
            FROM Sessions
            WHERE SessionHash = ?
        """, (session_hash,))
        user_uuid = [i for i in cursor][0]
    return get_user(uuid=user_uuid)

def get_user_by_spotify(client_id):
    with Database() as db:
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
    with Database() as db:
        db.execute("""
            DELETE FROM Users
            WHERE
        """ + f"Username = ?" if username else f'UUID = ?', (username or uuid,))

# Session methods
def create_session(ttl, user_uuid=None):
    session_token = utils.random_string(64)
    session_hash = sha256(session_token.encode()).hexdigest()

    with Database() as db:
        db.execute("""
            INSERT INTO Sessions(
                UserUUID,
                SessionHash,
                TTL
            )
            VALUES (?, ?, ?)
        """, (user_uuid, session_hash, ttl))
    return session_token

def get_sessions():
    with Database() as db:
        cursor = db.execute("""
            SELECT
                SessionHash
            FROM Sessions
            WHERE 1=1
        """)
        return [i for i in cursor]

def get_session(session_hash):
    with Database() as db:
        cursor = db.execute("""
            SELECT
                UserUUID,
                TTL
            FROM Sessions
            WHERE SessionHash = ?
        """, (session_hash,))
        sessions = [i for i in cursor]
        if not sessions:
            return {k[0]: None for k in cursor.description}
        return {k[0]: v for k, v in zip(cursor.description, sessions[0])}


def delete_session(session_hash):
    with Database() as db:
        db.execute("""
            DELETE FROM Sessions WHERE SessionHash = ?           
        """, (session_hash,))

def edit_user_to_session(session_hash, user_uuid=None):
    with Database() as db:
        db.execute("""
            UPDATE Sessions SET UserUUID = ? WHERE SessionHash = ?
        """, (user_uuid, session_hash))

# Tokens
def create_token(user_uuid, ttl):
    token = utils.random_string(128)
    token_hash = sha256(token.encode()).hexdigest()

    with Database() as db:
        db.execute("""
            INSERT INTO Tokens(
                TokenHash,
                UserUUID,
                TTL
            )
            VALUES (?, ?, ?)
        """,
        (token_hash, str(user_uuid), ttl))

def get_token(token_hash):
    with Database() as db:
        cursor = db.execute("""
            SELECT 
                t.TokenHash,
                t.TTL,
                u.*
            FROM Tokens as t
            LEFT OUTER JOIN Users as u
                ON u.UUID = t.UserUUID  
            WHERE t.TokenHash = ?
        """)
        return {k[0]: v for k, v in zip(cursor.description, cursor)}

def delete_token(token_hash):
    with Database() as db:
        db.execute("""
            DELETE
                *
            FROM Tokens
            WHERE token_hash = ?        
        """, (token_hash,))