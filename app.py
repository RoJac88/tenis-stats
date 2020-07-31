from flask import Flask, g
from db import get_db, query_db, make_db
from import_players import make_player_queries
from import_tournaments import make_tournaments
from import_matches import make_matches
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)


@app.cli.command('init')
def initialize():
    if os.path.isfile(Config.DB):
        print('Banco de dados já foi criado')
    else:
        print('Criando scripts...')
        make_player_queries()
        make_tournaments()
        make_matches()
        make_db()
        print('Banco de dados criado com sucesso')


@app.template_filter('atp_level')
def translate_atp_level(char):
    if char == 'G':
        return 'Grand Slams'
    elif char == 'A':
        return 'ATP Masters'
    elif char == 'D':
        return 'Davis Cups'


@app.before_request
def before_request():
    g.db = get_db()
    g.query_db = query_db


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


from routes import *
from api import *


if __name__ == "__main__":
    app.run(
        debug=True
    )
