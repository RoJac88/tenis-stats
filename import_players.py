import os
import csv
from config import Config

DIR = Config.CSV_DIR
PLAYER_INPUT = 'atp_players_amostra.csv'
PLAYER_OUTPUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'sql', '2-insert_players.sql'))


def write_insert_player(player_id, first_name, last_name, birthdate, hand,
                        country, output_file=False):
    birthdate = f"{birthdate[:4]}-{birthdate[4:6]}-{birthdate[6:8]}"
    if birthdate == '--':
        birthdate = '????-??-??'
    if len(country) == 0:
        country = '???'
    if len(hand) == 0:
        hand = 'U'
    sql = f'''INSERT OR IGNORE INTO Players (id, first_name, last_name, birthdate, hand, country)
        VALUES ({player_id}, '{first_name}', '{last_name}', '{birthdate}', '{hand}', '{country}');\n'''
    if output_file:
        output_file.write(sql)
    else:
        print(sql)
    return sql


def make_player_queries(output=PLAYER_OUTPUT):
    path = os.path.join(DIR, PLAYER_INPUT)
    print(path)
    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        with open(output, 'w', encoding='utf-8') as output_file:
            for i, row in enumerate(reader):
                write_insert_player(
                    row['player_id'],
                    row['first_name'],
                    row['last_name'],
                    row['birthdate'],
                    row['hand'],
                    row['country_code'],
                    output_file=output_file
                )
        print(f"Written sql to insert {i} players to {output}")


if __name__ == '__main__':
    make_player_queries()
