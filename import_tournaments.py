import os
import csv
from config import Config

DIR = Config.CSV_DIR
MATCHES = (match for match in os.listdir(DIR) if match[:11] == 'atp_matches')
T_OUTPUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'sql', '3-insert_tournaments.sql'))


def write_insert_tournament(t_id, t_year, t_name, atp, t_date, surface, output_file=False):
    sql = f'''INSERT OR IGNORE INTO Tournaments (tournament_id, tournament_year, t_name, atp_level, t_date, surface)
        VALUES ('{t_id}', {t_year}, '{t_name}', '{atp}', '{t_date}', '{surface}');\n'''
    if output_file:
        output_file.write(sql)
    else:
        print(sql)
    return sql


def read_tournaments(input_csv, found={}):
    reader = csv.DictReader(input_csv)
    for i, row in enumerate(reader):
        t_data = row['tourney_id'].split('-')
        if len(t_data) == 2:
            t_year, t_id = t_data
        else:
            t_year = t_data[0]
            t_id = '_'.join(t_data[1:])
        key = (t_year, t_id)
        if key not in found:
            t_name = row['tourney_name'].replace("'", "’")
            atp = row['tourney_level']
            if atp == 'M':
                atp = 'A'
            t_date = row['tourney_date']
            t_date = f"{t_date[:4]}-{t_date[4:6]}-{t_date[6:8]}"
            if t_date == '--':
                t_date = '????-??-??'
            surface = row['surface']
            if len(surface) == 0:
                surface = 'U'
            if surface == 'Carpet':
                surface = 'P'
            else:
                surface = surface[:1]
            found[key] = (t_id, t_year, t_name, atp, t_date, surface)
    return found


def make_tournaments():
    found = {}
    for match in MATCHES:
        with open(os.path.join(DIR, match), 'r') as source:
            found = read_tournaments(source, found=found)
    with open(T_OUTPUT, 'w', encoding='utf-8') as output:
        for values in found.values():
            write_insert_tournament(*values, output_file=output)
    print(f'Created queries to insert {len(found)} tournaments in {T_OUTPUT}')


if __name__ == '__main__':
    make_tournaments()
