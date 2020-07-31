from flask import g
from app import app

LIMIT = app.config.get('LIMIT')


def count_players():
    return g.query_db('SELECT COUNT(*) FROM Players', one=True)


def count_tournaments():
    return g.query_db('SELECT COUNT(*) FROM Tournaments', one=True)


def count_matches():
    return g.query_db('SELECT COUNT(*) FROM Matches', one=True)


def create_player(player_id, first_name, last_name, birthdate, hand, height, country, img):
    cur = g.db.cursor()
    sql = f'''INSERT INTO Players (id, first_name, last_name, birthdate, hand, height, country, img)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);\n'''
    cur.execute(sql, (player_id, first_name, last_name, birthdate, hand, height, country, img))
    g.db.commit()
    cur.close()


def update_player(old_id, new_id, first_name, last_name, birthdate, hand, height, country, img):
    cur = g.db.cursor()
    sql = f'''UPDATE Players
                SET id=?, first_name=?, last_name=?, birthdate=?, hand=?, height=?, country=?, img=?
                WHERE id=?'''
    cur.execute(sql, (new_id, first_name, last_name, birthdate, hand, height, country, img, old_id))
    g.db.commit()
    cur.close()


def remove_player(player_id):
    cur = g.db.cursor()
    sql = 'DELETE FROM Players WHERE id=?'
    cur.execute(sql, (player_id,))
    g.db.commit()
    cur.close()


def read_player(player_id):
    return g.query_db('SELECT * FROM Players WHERE id = ?;',
                      (player_id,), one=True)


def read_players(country=None, first_name=None, last_name=None, page=1, limit=LIMIT):
    if limit > LIMIT:
        limit = LIMIT
    filters = []
    if country:
        filters.append(f"country = '{country}'")
    if first_name:
        filters.append(f"first_name = '{first_name}'")
    if last_name:
        filters.append(f"last_name = '{last_name}'")
    if len(filters) == 0:
        return g.query_db(f'SELECT * FROM Players ORDER BY id LIMIT {limit} OFFSET {(int(page) - 1) * limit};')
    filters = f"WHERE ({' AND '.join(filters)})"
    return g.query_db(f'SELECT * FROM Players {filters} ORDER BY id LIMIT {limit} OFFSET {(int(page) - 1) * limit};')


def search_player_names(query):
    return g.query_db('''
        SELECT id, first_name, last_name FROM Players
        WHERE (INSTR(first_name || ' ' || last_name, ?) > 0)
        ''', (query,))


def read_players_wins(limit=LIMIT):
    if limit > LIMIT:
        limit = LIMIT
    return g.query_db('''
        SELECT * FROM (
            SELECT winner_id, count(winner_id) as wins FROM (
                SELECT winner_id FROM Matches
            )
                group by winner_id
                order by wins desc
        )
        INNER JOIN (SELECT first_name, last_name, country, id, birthdate FROM Players) 
        ON winner_id = id
        LIMIT ?;
    ''', (limit,))


def create_tournament(t_id, t_year, t_name, cat, t_date, surface):
    cur = g.db.cursor()
    sql = f'''INSERT INTO Tournaments (tournament_id, tournament_year, t_name, atp_level, t_date, surface)
        VALUES (?, ?, ?, ?, ?, ?);\n'''
    cur.execute(sql, (t_id, t_year, t_name, cat, t_date, surface))
    g.db.commit()
    cur.close()


def update_tournament(old_id, old_year, t_id, t_year, t_name, cat, t_date, surface):
    cur = g.db.cursor()
    sql = f'''UPDATE Tournaments
        SET tournament_id=?, tournament_year=?, t_name=?, atp_level=?, t_date=?, surface=?
        WHERE tournament_id=? AND tournament_year=?;\n'''
    cur.execute(sql, (t_id, t_year, t_name, cat, t_date, surface, old_id, old_year))
    g.db.commit()
    cur.close()


def remove_tournament(t_id, t_year):
    cur = g.db.cursor()
    sql = 'DELETE FROM Tournaments WHERE tournament_id=? AND tournament_year=?'
    cur.execute(sql, (t_id, t_year,))
    g.db.commit()
    cur.close()


def read_tournament(t_id, t_year):
    return g.query_db(
        '''SELECT * FROM Tournaments
        LEFT JOIN (SELECT t_id, t_year, t_round, winner_id, loser_id FROM Matches) ON (tournament_id=t_id AND tournament_year=t_year AND t_round='F')
        LEFT JOIN (SELECT id as w_id, country as w_fed, first_name as w_fname, last_name as w_lname FROM Players) ON w_id=winner_id
        LEFT JOIN (SELECT id as r_id, country as r_fed, first_name as r_fname, last_name as r_lname FROM Players) ON r_id=loser_id
        WHERE tournament_id = ? AND tournament_year = ?;''',
        (t_id, t_year,), one=True)


def read_tournaments_all(page=1, limit=LIMIT):
    if limit > LIMIT:
        limit = LIMIT
    return g.query_db('''SELECT * FROM Tournaments
        LEFT JOIN (SELECT t_id, t_year, t_round, winner_id, loser_id FROM Matches) ON (tournament_id=t_id AND tournament_year=t_year AND t_round='F')
        LEFT JOIN (SELECT id as w_id, country as w_fed, first_name as w_fname, last_name as w_lname FROM Players) ON w_id=winner_id
        LEFT JOIN (SELECT id as r_id, country as r_fed, first_name as r_fname, last_name as r_lname FROM Players) ON r_id=loser_id
        LIMIT ? OFFSET ?;''', (limit, (page-1)*limit))


def read_tournament_names_id():
    return g.query_db('SELECT DISTINCT tournament_id, t_name FROM Tournaments')


def read_tournaments_by_name(t_name):
    return g.query_db('''SELECT * FROM Tournaments
        LEFT JOIN (SELECT t_id, t_year, t_round, winner_id, loser_id FROM Matches) ON (tournament_id=t_id AND tournament_year=t_year AND t_round='F')
        LEFT JOIN (SELECT id as w_id, country as w_fed, first_name as w_fname, last_name as w_lname FROM Players) ON w_id=winner_id
        LEFT JOIN (SELECT id as r_id, country as r_fed, first_name as r_fname, last_name as r_lname FROM Players) ON r_id=loser_id
        WHERE t_name = ?
        ORDER BY t_date DESC''', (t_name,))


def read_tournament_names_by_surface(surface):
    return g.query_db(
        '''SELECT DISTINCT (t_name) FROM Tournaments WHERE (surface = ? AND atp_level != 'D');''',
        (surface,))


def read_tournament_names_by_cat(cat):
    return g.query_db(
        '''SELECT DISTINCT (t_name) FROM Tournaments WHERE (atp_level = ?);''', (cat,))


def read_tournaments_by_cat(cat):
    return g.query_db(
        f'''SELECT * FROM Tournaments
        LEFT JOIN (SELECT t_id, t_year, t_round, winner_id, loser_id FROM Matches) ON (tournament_id=t_id AND tournament_year=t_year AND t_round='F')
        LEFT JOIN (SELECT id as w_id, country as w_fed, first_name as w_fname, last_name as w_lname FROM Players) ON w_id=winner_id
        LEFT JOIN (SELECT id as r_id, country as r_fed, first_name as r_fname, last_name as r_lname FROM Players) ON r_id=loser_id
        WHERE atp_level = ?
        ORDER BY t_date DESC''', (cat,))


def read_last_t_match(t_id, t_year):
    return g.query_db('SELECT match_number FROM Matches WHERE t_id=? AND t_year=? ORDER BY match_number DESC LIMIT 1', (t_id, t_year, ), one=True)


def create_match(*args):
    cur = g.db.cursor()
    sql = f'''INSERT INTO Matches (match_number, t_id, t_year, winner_id, loser_id, score, best_of, t_round,
                 w_ace, w_df, w_svpt, w_1stIn, w_1stWon, w_2ndWon, w_SvGms, w_bpSaved, w_bpFaced,
                 l_ace, l_df, l_svpt, l_1stIn, l_1stWon, l_2ndWon, l_SvGms, l_bpSaved, l_bpFaced)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);\n'''
    cur.execute(sql, (*args,))
    g.db.commit()
    cur.close()


def update_match(*args):
    cur = g.db.cursor()
    sql = f'''UPDATE Matches
            SET match_number=?, t_id=?, t_year=?, winner_id=?, loser_id=?, score=?, best_of=?, t_round=?,
            w_ace=?, w_df=?, w_svpt=?, w_1stIn=?, w_1stWon=?, w_2ndWon=?, w_SvGms=?, w_bpSaved=?, w_bpFaced=?,
            l_ace=?, l_df=?, l_svpt=?, l_1stIn=?, l_1stWon=?, l_2ndWon=?, l_SvGms=?, l_bpSaved=?, l_bpFaced=?
            WHERE (match_number=? AND t_id=? AND t_year=?);\n'''
    cur.execute(sql, (*args,))
    g.db.commit()
    cur.close()


def read_match(match_number, t_id, t_year):
    return g.query_db(
        '''SELECT * FROM Matches
        LEFT JOIN (SELECT tournament_id, atp_level, tournament_year, t_name, t_date, surface FROM Tournaments) ON Matches.t_id = tournament_id AND Matches.t_year = tournament_year
        LEFT JOIN (SELECT id as w_id, first_name as winner_fname, last_name as winner_lname, country as w_fed FROM Players) ON Matches.winner_id = w_id
        LEFT JOIN (SELECT id as l_id, first_name as loser_fname, last_name as loser_lname, country as l_fed FROM Players) ON Matches.loser_id = l_id
        WHERE (match_number = ? AND t_id=? AND t_year=?);''',
        (match_number, t_id, t_year), one=True)


def remove_match(match_number, t_id, t_year):
    cur = g.db.cursor()
    sql = 'DELETE FROM Matches WHERE (match_number = ? AND t_id=? AND t_year=?);'
    cur.execute(sql, (match_number, t_id, t_year,))
    g.db.commit()
    cur.close()


def clear_tournament_matches(t_id, t_year):
    cur = g.db.cursor()
    sql = 'DELETE FROM Matches WHERE (t_id=? AND t_year=?);'
    cur.execute(sql, (t_id, t_year,))
    g.db.commit()
    cur.close()


def read_matches(start_year=1900, end_year=2100, page=1, limit=LIMIT):
    if limit > LIMIT:
        limit = LIMIT
    return g.query_db(f'''
        SELECT atp_level, t_id, t_name, t_year, match_number, t_round, w_fed, w_id, winner_fname, winner_lname, l_fed, l_id, loser_fname, loser_lname, surface FROM
            (SELECT * FROM Matches
            LEFT JOIN (SELECT tournament_id, tournament_year, t_name, t_date, surface, atp_level FROM Tournaments) ON t_id = tournament_id AND t_year = tournament_year
            LEFT JOIN (SELECT id as w_id, first_name as winner_fname, last_name as winner_lname, country as w_fed FROM Players) ON winner_id = w_id
            LEFT JOIN (SELECT id as l_id, first_name as loser_fname, last_name as loser_lname, country as l_fed FROM Players) ON loser_id = l_id
            WHERE (t_year BETWEEN ? AND ?) ORDER BY t_date DESC
            LIMIT ? OFFSET ?);
        ''', (start_year, end_year, limit, (page-1)*limit), )


def read_matches_from_player(player_id, page=1, limit=LIMIT):
    if limit > LIMIT:
        limit = LIMIT
    return g.query_db(
        '''SELECT * FROM Matches
        LEFT JOIN (SELECT tournament_id, tournament_year, t_name, t_date, surface, atp_level FROM Tournaments) ON Matches.t_id = tournament_id AND Matches.t_year = tournament_year
        LEFT JOIN (SELECT id as w_id, first_name as winner_fname, last_name as winner_lname, country as w_fed FROM Players) ON Matches.winner_id = w_id
        LEFT JOIN (SELECT id as l_id, first_name as loser_fname, last_name as loser_lname, country as l_fed FROM Players) ON Matches.loser_id = l_id
        WHERE (w_id=? OR l_id=?)
        ORDER BY t_date DESC
        LIMIT ? OFFSET ?
        ''', (player_id, player_id, limit, limit*(page-1)))


def read_matches_from_tournament(t_id, t_year, player_id=None):
    if player_id:
        return g.query_db(
        '''SELECT * FROM Matches
        LEFT JOIN (SELECT tournament_id, tournament_year, t_name, t_date, atp_level, surface FROM Tournaments) ON Matches.t_id = tournament_id AND Matches.t_year = tournament_year
        LEFT JOIN (SELECT id as w_id, first_name as winner_fname, last_name as winner_lname, country as w_fed FROM Players) ON Matches.winner_id = w_id
        LEFT JOIN (SELECT id as l_id, first_name as loser_fname, last_name as loser_lname, country as l_fed FROM Players) ON Matches.loser_id = l_id
        WHERE (tournament_id=? AND t_year=? AND (w_id=? OR l_id=?))
        ORDER BY match_number DESC''', (t_id, t_year, player_id, player_id))
    else:
        return g.query_db(
        '''SELECT * FROM Matches
        LEFT JOIN (SELECT tournament_id, tournament_year, t_name, t_date, atp_level, surface FROM Tournaments) ON Matches.t_id = tournament_id AND Matches.t_year = tournament_year
        LEFT JOIN (SELECT id as w_id, first_name as winner_fname, last_name as winner_lname, country as w_fed FROM Players) ON Matches.winner_id = w_id
        LEFT JOIN (SELECT id as l_id, first_name as loser_fname, last_name as loser_lname, country as l_fed FROM Players) ON Matches.loser_id = l_id
        WHERE (tournament_id=? AND t_year=?)
        ORDER BY match_number DESC''', (t_id, t_year))


def finals_won_by_player(winner_id):
    return g.query_db(
        '''
        SELECT tournament_year, tournament_id, t_name, surface, atp_level, l_id, loser_fname, loser_lname, l_fed FROM (
            SELECT * FROM Matches
            INNER JOIN (SELECT tournament_id, atp_level, tournament_year, t_name, t_date, surface FROM Tournaments) ON Matches.t_id = tournament_id AND Matches.t_year = tournament_year
            INNER JOIN (SELECT id as l_id, first_name as loser_fname, last_name as loser_lname, country as l_fed FROM Players) ON Matches.loser_id = l_id
            WHERE (Matches.t_round = 'F' AND winner_id=?)
        )
        ''', (winner_id,))


def count_player_tournament_wins(player_id):
    result = g.query_db(
        "SELECT COUNT (*) FROM Matches WHERE (Matches.t_round = 'F' AND winner_id=?)",
        (player_id,), one=True)
    return result['COUNT (*)']


def count_player_slam_wins(player_id):
    result = g.query_db(
        '''SELECT COUNT (*) FROM Matches
        INNER JOIN (SELECT tournament_id, tournament_year, atp_level FROM Tournaments) ON Matches.t_id = tournament_id AND Matches.t_year = tournament_year
        WHERE (Matches.t_round = 'F' AND atp_level='G' AND winner_id=?)''',
        (player_id,), one=True)
    return result['COUNT (*)']


def count_player_matches(player_id):
    result = g.query_db(
        "SELECT COUNT (*) FROM Matches WHERE (loser_id=? OR winner_id=?)",
        (player_id, player_id), one=True)
    return result['COUNT (*)']


def player_score(player_id):
    finals_played = g.query_db("SELECT COUNT (*) FROM Matches WHERE (Matches.t_round = 'F' AND (winner_id=? OR loser_id=?))",
                        (player_id, player_id), one=True)
    n_finals_won = count_player_slam_wins(player_id)
    return (n_finals_won, finals_played['COUNT (*)'])


def read_player_countries():
    return g.query_db("SELECT DISTINCT country FROM Players")
