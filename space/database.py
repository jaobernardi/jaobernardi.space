# database.py * This file handles all calls to the database.
from datetime import datetime
import sqlite3

from .config import Config
import json

# Currently i'll work with a local database 
config = Config()
