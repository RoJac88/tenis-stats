import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    DB = os.path.join(BASE_DIR, 'database.db')
    SQL_DIR = os.path.join(BASE_DIR, 'sql')
    CSV_DIR = os.path.abspath(os.path.join(BASE_DIR, 'csv'))
    LIMIT = 100
    SECRET_KEY = 'chave-insegura-pra-cacete'
