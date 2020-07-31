import os
import sqlite3
from flask import g
from sqlite3 import Error
from config import Config

DATABASE = Config.DB
SQL_DIR = Config.SQL_DIR


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = make_dicts
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def make_db():
    conn = sqlite3.connect(DATABASE)
    print('Construindo Banco de Dados')
    arquivos = os.listdir(SQL_DIR)
    arquivos.sort()
    try:
        for arq in arquivos:
            with open(os.path.join(SQL_DIR, arq), 'r') as arquivo:
                print('Aplicando script:', arq)
                sql = arquivo.read()
                c = conn.cursor()
                c.executescript(sql)
    except Error as e:
        print(e)


if __name__ == "__main__":
    make_db()
