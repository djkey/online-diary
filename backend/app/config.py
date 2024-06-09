import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv('HOST')
    DB_USER = os.getenv('USER')
    DB_PASSWORD = os.getenv('PASSWORD')
    DB_NAME = os.getenv('DBNAME')
    SECRET_KEY = os.urandom(24)
