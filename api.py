from app import app
from flask import jsonify, request
from dao import search_player_names


@app.route('/api/players')
def api_players():
    query = request.args.get('query').title()
    if query and len(query) >= 3:
        return jsonify(search_player_names(query))
    else:
        return 'busca inválida', 400
