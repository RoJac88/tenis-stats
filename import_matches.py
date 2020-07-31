import os
import csv
from config import Config

DIR = Config.CSV_DIR
MATCHES = (match for match in os.listdir(DIR) if match[:11] == 'atp_matches')
M_OUTPUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'sql', '4-insert_matches.sql'))


def write_insert_match(match_number, t_id, t_year, winner_id, loser_id, score,
                       best_of, t_round, w_ace=None, w_df=None, w_svpt=None,
                       w_1stIn=None, w_1stWon=None, w_2ndWon=None,
                       w_SvGms=None, w_bpSaved=None, w_bpFaced=None, mins=None,
                       l_ace=None, l_df=None, l_svpt=None, l_1stIn=None,
                       l_1stWon=None, l_2ndWon=None, l_SvGms=None,
                       l_bpSaved=None, l_bpFaced=None, output_file=False):
    sql = f'''INSERT OR IGNORE INTO Matches (
            match_number,
            t_id,
            t_year,
            winner_id,
            loser_id,
            score,
            best_of,
            t_round,
            w_ace,
            w_df,
            w_svpt,
            w_1stIn,
            w_1stWon,
            w_2ndWon,
            w_SvGms,
            w_bpSaved,
            w_bpFaced,
            l_ace,
            l_df,
            l_svpt,
            l_1stIn,
            l_1stWon,
            l_2ndWon,
            l_SvGms,
            l_bpSaved,
            l_bpFaced,
            mins
            )
        VALUES (
            {match_number},
            '{t_id}',
            {t_year},
            {winner_id},
            {loser_id},
            '{score}',
            '{best_of}',
            '{t_round}',
            {w_ace},
            {w_df},
            {w_svpt},
            {w_1stIn},
            {w_1stWon},
            {w_2ndWon},
            {w_SvGms},
            {w_bpSaved},
            {w_bpFaced},
            {l_ace},
            {l_df},
            {l_svpt},
            {l_1stIn},
            {l_1stWon},
            {l_2ndWon},
            {l_SvGms},
            {l_bpSaved},
            {l_bpFaced},
            {mins});\n'''
    if output_file:
        output_file.write(sql)
    else:
        print(sql)
    return sql


def read_matches(input_csv, found={}, stat_map={}):
    reader = csv.DictReader(input_csv)
    for row in reader:
        t_data = row['tourney_id'].split('-')
        if len(t_data) == 2:
            t_year, t_id = t_data
        else:
            t_year = t_data[0]
            t_id = '_'.join(t_data[1:])
        match_number = int(row['match_num'])
        key = (match_number, t_id, t_year)
        if key not in found:
            stats = {}
            winner_id = int(row['winner_id'])
            loser_id = int(row['loser_id'])
            score = row['score']
            best_of = row['best_of']
            t_round = row['round']
            stats['mins'] = row.get('minutes') or 'NULL'
            stats['w_ace'] = row.get('w_ace') or 'NULL'
            stats['w_df'] = row.get('w_df') or 'NULL'
            stats['w_svpt'] = row.get('w_svpt') or 'NULL'
            stats['w_1stIn'] = row.get('w_1stIn') or 'NULL'
            stats['w_1stWon'] = row.get('w_1stWon') or 'NULL'
            stats['w_2ndWon'] = row.get('w_2ndWon') or 'NULL'
            stats['w_SvGms'] = row.get('w_SvGms') or 'NULL'
            stats['w_bpSaved'] = row.get('w_bpSaved') or 'NULL'
            stats['w_bpFaced'] = row.get('w_bpFaced') or 'NULL'
            stats['l_ace'] = row.get('l_ace') or 'NULL'
            stats['l_df'] = row.get('l_df') or 'NULL'
            stats['l_svpt'] = row.get('l_svpt') or 'NULL'
            stats['l_1stIn'] = row.get('l_1stIn') or 'NULL'
            stats['l_1stWon'] = row.get('l_1stWon') or 'NULL'
            stats['l_2ndWon'] = row.get('l_2ndWon') or 'NULL'
            stats['l_SvGms'] = row.get('l_SvGms') or 'NULL'
            stats['l_bpSaved'] = row.get('l_bpSaved') or 'NULL'
            stats['l_bpFaced'] = row.get('l_bpFaced') or 'NULL'
            found[key] = (*key, winner_id, loser_id, score, best_of, t_round)
            stat_map[key] = stats
    return found, stat_map


def make_matches():
    found = {}
    stats = {}
    for match in MATCHES:
        with open(os.path.join(DIR, match), 'r', encoding='utf-8') as source:
            found, stats = read_matches(source, found=found, stat_map=stats)
    with open(M_OUTPUT, 'w', encoding='utf-8') as output:
        for key, values in found.items():
            write_insert_match(*values, **stats[key], output_file=output)
    print(f'Created queries to insert {len(found)} matches in {M_OUTPUT}')


if __name__ == '__main__':
    make_matches()
