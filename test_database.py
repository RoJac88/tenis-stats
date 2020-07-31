import os
import sqlite3
import csv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = make_dicts
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def insert_winners():
    ts = query_db('''
        SELECT tournament_id, tournament_year FROM Tournaments
        ''')
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    for t in ts:
        winner = query_db('''
                          SELECT winner_id FROM Matches
                          WHERE (t_id = ? AND t_year = ? AND t_round='F')''',
                          (t['tournament_id'], t['tournament_year'],), one=True)
        if winner:
            winner = winner.get('winner_id') or None
            assert winner is not None
            cur.execute('''
                        UPDATE Tournaments SET winner = ?
                        WHERE (tournament_id = ? AND tournament_year = ?)''',
                        (winner, t['tournament_id'], t['tournament_year'],))
    db.commit()
    cur.close()


def insert_runnerups():
    ts = query_db('''
        SELECT tournament_id, tournament_year FROM Tournaments
        ''')
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    for t in ts:
        runnerup = query_db('''
                          SELECT loser_id FROM Matches
                          WHERE (t_id = ? AND t_year = ? AND t_round='F')''',
                          (t['tournament_id'], t['tournament_year'],), one=True)
        if runnerup:
            runnerup = runnerup.get('loser_id') or None
            assert runnerup is not None
            cur.execute('''
                        UPDATE Tournaments SET runnerup = ?
                        WHERE (tournament_id = ? AND tournament_year = ?)''',
                        (runnerup, t['tournament_id'], t['tournament_year'],))
    db.commit()
    cur.close()


def drop_table():
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    cur.execute("DROP TABLE Tournaments")
    db.commit()
    cur.close()


def add_tournament_runnerup():
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    cur.execute("ALTER TABLE Tournaments ADD runnerup INT")
    db.commit()


def add_match_indexes():
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    '''
    cur.execute("ALTER TABLE Matches ADD idx INT")
    db.commit()
    print("Added idx")
    '''
    matches = query_db('SELECT * FROM Matches')
    print('Populating indexes...')
    for i, m in enumerate(matches, 1):
        match_number = m['match_number']
        t_id = m['t_id']
        t_year = m['t_year']
        cur.execute(f'''
        UPDATE Matches SET idx = ?
        WHERE (match_number = ? AND t_id = ? AND t_year = ?)
        ''', (i, match_number, t_id, t_year,))
        if i % 5000 == 0:
            print(f"populated {i}/176950 ...")
    db.commit()
    cur.close()


def export_player_imgs(filename='export.csv'):
    with open(os.path.join(BASE_DIR, filename), 'w', newline='') as output:
        players = query_db('SELECT id, img FROM Players WHERE img IS NOT NULL')
        fieldnames = ('id', 'img', )
        csv_writer = csv.DictWriter(output, fieldnames=fieldnames)
        csv_writer.writeheader()
        for player in players:
            csv_writer.writerow(player)
    print('URLs exportadas para:', filename)


def import_player_imgs(filename='player_imgs.csv'):
    db = get_db()
    cur = db.cursor()
    with open(os.path.join(BASE_DIR, filename), 'r', newline='') as source:
        csv_reader = csv.DictReader(source)
        for row in csv_reader:
            player_id = row['id']
            player = query_db('SELECT * FROM Players WHERE id = ?', (player_id, ), one=True)
            if player:
                cur.execute('UPDATE Players SET img = ? WHERE id = ?', (row['img'], player_id))
    db.commit()
    cur.close()


def export_players(filename='players.csv'):
    with open(os.path.join(BASE_DIR, filename), 'w', newline='') as output:
        players = query_db('''
        SELECT * FROM Players
        INNER JOIN (
            SELECT DISTINCT pid FROM
            (
                SELECT Count(*), winner_id as pid FROM Matches
                GROUP BY winner_id
                UNION
                SELECT Count(*), loser_id as pid FROM Matches
                GROUP BY loser_id
            )) ON Players.id=pid
        ''')
        fieldnames = ('player_id', 'first_name', 'last_name', 'birthdate', 'hand', 'country_code')
        csv_writer = csv.DictWriter(output, fieldnames=fieldnames)
        csv_writer.writeheader()
        for player in players:
            bdate = player['birthdate']
            bdate = bdate.split('-')
            bdate = ''.join(bdate)
            row = {
                'player_id': player['id'],
                'first_name': player['first_name'],
                'last_name': player['last_name'],
                'birthdate': bdate,
                'hand': player['hand'],
                'country_code': player['country']
            }
            csv_writer.writerow(row)


if __name__ == '__main__':
    import_player_imgs(filename='export.csv')
