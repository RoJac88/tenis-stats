from datetime import date
from app import app
from dao import count_players, count_tournaments, count_matches, read_player, \
    read_tournament, read_players, read_match, read_matches, \
    read_tournaments_by_cat, read_matches_from_player, remove_tournament, \
    read_matches_from_tournament, count_player_tournament_wins, \
    count_player_slam_wins, count_player_matches, create_tournament, \
    read_tournament_names_by_surface, read_tournaments_by_name, \
    read_tournament_names_by_cat, read_player_countries, read_players_wins, \
    create_player, update_player, remove_player, read_tournaments_all, \
    update_tournament, read_tournament_names_id, read_last_t_match, \
    create_match, update_match, remove_match, clear_tournament_matches
from flask import abort, render_template, request, redirect, url_for, flash
from helpers import get_next_prev_links

LIMIT = app.config.get('LIMIT')


@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html'), 405


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/')
def home():
    stats = [count_players(), count_tournaments(), count_matches()]
    stats = [stat['COUNT(*)'] for stat in stats]
    return render_template('home.html', active='home', stats=stats)


@app.route('/entrar/')
def login():
    return render_template('login.html')


@app.route('/tenistas/<player_id>/')
def view_player(player_id):
    player = read_player(player_id)
    if player:
        stats = {}
        stats['slams'] = count_player_slam_wins(player_id)
        stats['titles'] = count_player_tournament_wins(player_id)
        stats['matches'] = count_player_matches(player_id)
        matches = read_matches_from_player(player_id, limit=7)
        return render_template('player_profile.html', active='players', player=player, stats=stats, matches=matches)
    else:
        abort(404)


@app.route('/tenistas/')
def player_menu():
    players = read_players_wins(limit=10)
    feds = [c['country'] for c in read_player_countries()]
    if '???' in feds:
        feds.remove('???')
    return render_template('players_menu.html', active='players', feds=sorted(feds), players=players)


@app.route('/torneios/<t_code>/')
def view_tournament(t_code):
    _t = t_code.split('-')
    if len(_t) != 2:
        abort(400)
    t_year, t_id = _t
    tournament = read_tournament(t_id, t_year)
    if tournament:
        matches = read_matches_from_tournament(t_id, t_year)
        return render_template('tournament_profile.html', active='tournaments',
                               tournament=tournament, matches=matches)
    else:
        abort(404)


@app.route('/torneios/')
def view_tournaments():
    t_name = request.args.get('nome') or None
    atp_level = request.args.get('cat') or None
    if t_name and atp_level:
        tournaments = read_tournaments_by_name(t_name)
        tabs = read_tournament_names_by_cat(atp_level)
        tabs = [tab['t_name'] for tab in tabs]
        return render_template('tournament_editions.html', tournaments=tournaments, tabs=sorted(tabs), active='tournaments', active_tab=t_name, atp_level=atp_level)
    if t_name:
        tournaments = read_tournaments_by_name(t_name)
        return render_template('tournament_editions.html', tournaments=tournaments, active='tournaments', overline=t_name)
    if atp_level:
        tournaments = read_tournaments_by_cat(atp_level)
        tabs = read_tournament_names_by_cat(atp_level)
        tabs = [tab['t_name'] for tab in tabs]
        return render_template('tournament_editions.html', tournaments=tournaments, tabs=sorted(tabs), active='tournaments', active_tab='Todos', atp_level=atp_level)
    t_names = {}
    t_names['grass'] = [d['t_name'] for d in read_tournament_names_by_surface('G')]
    t_names['clay'] = [d['t_name'] for d in read_tournament_names_by_surface('C')]
    t_names['hard'] = [d['t_name'] for d in read_tournament_names_by_surface('H')]
    t_names['carpet'] = [d['t_name'] for d in read_tournament_names_by_surface('P')]
    return render_template('tournaments_menu.html', active='tournaments', t_names=t_names)


@app.route('/partidas/<player_id>/')
def view_player_matches(player_id):
    page = request.args.get('page') or 1
    page = int(page)
    player = read_player(player_id)
    matches = read_matches_from_player(player_id, page=page)
    if len(matches) == 0:
        abort(404)
    else:
        parameters = {'player_id': player_id}
        previous, _next = get_next_prev_links('view_player_matches', page, matches, LIMIT, parameters=parameters)
        return render_template('player_matches.html', player=player, matches=matches, page=page, next=_next, previous=previous, active='matches')


@app.route('/partidas/<player_id>/<m_code>/')
def view_match(m_code, player_id):
    _m = m_code.split('-')
    if len(_m) != 3:
        abort(400)
    match_number, t_id, t_year = _m
    match = read_match(match_number, t_id, t_year)
    if match:
        split_score = []
        sets = match['score'].split(' ')
        for _set in sets:
            split_score.append(tuple(_set.split('-')))
        match['split_score'] = split_score
        return render_template('view_match.html', match=match)
    else:
        abort(404)


@app.route('/partidas/')
def view_matches():
    page = request.args.get('page') or 1
    page = int(page)
    player = request.args.get('tenista') or None
    t_code = request.args.get('torneio') or None
    if t_code:
        _t = t_code.split('-')
        if len(_t) != 2:
            abort(400)
        t_year, t_id = _t
    if player and t_code:
        matches = read_matches_from_player(page=page)
        previous, _next = get_next_prev_links('view_matches', page, matches, LIMIT)
        return render_template('matches_list.html', matches=matches, active='matches', page=page, previous=previous, next=_next)
    if player:
        matches = read_matches_from_player(player, page=page)
        if len(matches) == 0:
            abort(404)
        else:
            previous, _next = get_next_prev_links('view_matches', page, matches, LIMIT)
            return render_template('matches_list.html', matches=matches, active='matches', page=page, previous=previous, next=_next)
    if t_code:
        matches = read_matches(page=page)
        previous, _next = get_next_prev_links('view_matches', page, matches, LIMIT)
        return render_template('matches_list.html', matches=matches, active='matches', page=page, previous=previous, next=_next)
    matches = read_matches(page=page)
    previous, _next = get_next_prev_links('view_matches', page, matches, LIMIT)
    return render_template('matches_list.html', matches=matches, active='matches', page=page, previous=previous, next=_next)


@app.route('/rankings/')
def ranking_menu():
    return render_template('rankings_menu.html', active='rankings')


@app.route('/sobre/')
def about():
    return render_template('about.html', active='about')


@app.route('/admin/tenistas/alterar/<player_id>/', methods=['GET', 'POST'])
def edit_player(player_id):
    player = read_player(player_id)
    if not player:
        abort(404)
    if request.method == 'GET':
        return render_template('player_edit.html', errors={}, player=player, active='players')
    if request.method == 'POST':
        errors = {}
        REQ = 'Campo obrigatório'
        img = request.form.get('img')
        hand = request.form.get('hand').upper() or 'U'
        height = request.form.get('height')
        if height:
            try:
                height = int(height)
            except ValueError:
                errors['height'] = 'Valor inválido'
            if height < 0 or height > 300:
                errors['height'] = 'min 0cm, max 300cm'
        else:
            height = 'NULL'
        fed = request.form.get('fed')
        if not fed or not len(fed) == 3:
            errors['fed'] = 'Deve ter 3 letras'
        first_name = request.form.get('firstname')
        if not first_name or not len(first_name.strip()) > 0:
            errors['first_name'] = REQ
        last_name = request.form.get('lastname')
        if not last_name or not len(last_name.strip()) > 0:
            errors['last_name'] = REQ
        bdate = request.form.get('bdate')
        if not bdate:
            errors['bdate'] = REQ
        else:
            try:
                date.fromisoformat(bdate)
            except ValueError:
                errors['bdate'] = 'Data inválida'
        pid = request.form.get('id')
        if not pid:
            errors['id'] = REQ
        else:
            try:
                _player = read_player(int(pid))
            except ValueError:
                errors['id'] = 'ID inválido'
            if int(player_id) != int(pid) and _player:
                errors['id'] = 'ID em uso'
        if len(errors) == 0:
            update_player(
                new_id=int(pid),
                first_name=first_name.title(),
                last_name=last_name.title(),
                birthdate=bdate,
                hand=hand,
                height=height,
                country=fed,
                img=img,
                old_id=player_id
                )
            if not int(pid) == int(player_id):
                flash(f'ID alterado: {player_id} => {pid}', 'warning')
            flash('Tenista atualizado!', 'success')
            return redirect(url_for('view_player', player_id=int(pid)))
        else:
            flash('Erros no formulário!', 'error')
            return render_template('player_edit.html', errors=errors, player=player, active='players')


@app.route('/admin/tenistas/novo/', methods=['GET', 'POST'])
def new_player():
    errors = {}
    if request.method == 'POST':
        REQ = 'Campo obrigatório'
        img = request.form.get('img')
        hand = request.form.get('hand').upper() or 'U'
        height = request.form.get('height')
        if height:
            try:
                height = int(height)
            except ValueError:
                errors['height'] = 'Valor inválido'
            if height < 0 or height > 300:
                errors['height'] = 'min 0cm, max 300cm'
        fed = request.form.get('fed')
        if not fed or not len(fed) == 3:
            errors['fed'] = 'Deve ter 3 letras'
        first_name = request.form.get('firstname')
        if not first_name or not len(first_name.strip()) > 0:
            errors['first_name'] = REQ
        last_name = request.form.get('lastname')
        if not last_name or not len(last_name.strip()) > 0:
            errors['last_name'] = REQ
        bdate = request.form.get('bdate')
        if not bdate:
            errors['bdate'] = REQ
        else:
            try:
                date.fromisoformat(bdate)
            except ValueError:
                errors['bdate'] = 'Data inválida'
        pid = request.form.get('id')
        if not pid:
            errors['id'] = REQ
        else:
            try:
                _player = read_player(int(pid))
            except ValueError:
                errors['id'] = 'ID inválido'
            if _player:
                errors['id'] = 'ID em uso'
        if len(errors) == 0:
            create_player(
                player_id=int(pid),
                first_name=first_name.title(),
                last_name=last_name.title(),
                birthdate=bdate,
                hand=hand,
                height=height,
                country=fed,
                img=img
                )
            flash('Tenista inserido!', 'success')
            return redirect(url_for('view_player', player_id=int(pid)))
        else:
            flash('Erros no formulário!', 'error')
        return render_template('player_new.html', active='players', errors=errors)
    return render_template('player_new.html', active='players', errors=errors)


@app.route('/admin/tenistas/remover/<player_id>/')
def delete_player(player_id):
    player = read_player(player_id)
    if not player:
        abort(404)
    remove_player(player_id)
    flash(f'Tenista {player_id} removido!', 'success')
    return redirect(url_for('player_menu'))


@app.route('/admin/tenistas/')
def dump_players():
    page = request.args.get('page') or 1
    page = int(page)
    country = request.args.get('fed') or None
    if country:
        country = country.upper()
    first_name = request.args.get('prenome') or None
    if first_name:
        first_name = first_name.title()
    last_name = request.args.get('sobrenome') or None
    if last_name:
        last_name = last_name.title()
    players = read_players(country=country, first_name=first_name, last_name=last_name, page=page)
    previous, _next = get_next_prev_links('dump_players', page, players, LIMIT, parameters={'fed': country})
    return render_template('players_list.html', players=players, active='players', page=page, previous=previous, next=_next)


@app.route('/admin/torneios/novo/', methods=['GET', 'POST'])
def new_tournament():
    if request.method == 'POST':
        errors = {}
        REQ = 'Campo obrigatório'
        t_id = request.form.get('t-id')
        if not t_id:
            errors['t-id'] = REQ
        t_id = t_id.replace('-', '_')
        t_year = request.form.get('t-year')
        if not t_year:
            errors['t-year'] = REQ
        else:
            try:
                int(t_year)
            except ValueError:
                errors['t-year'] = 'Valor inválido'
        if t_id and t_year:
            tournament = read_tournament(t_id, t_year)
            if tournament:
                errors['t-id'] = 'Em uso'
                errors['t-year'] = 'Em uso'
        t_name = request.form.get('t-name')
        if not t_name:
            errors['t-name'] = REQ
        t_date = request.form.get('t-date')
        if not t_date:
            errors['t-date'] = REQ
        if len(errors) == 0:
            create_tournament(t_id, t_year, t_name, request.form['cat'], t_date, request.form['surface'])
            flash('Torneio inserido!', 'success')
            return redirect(url_for('view_tournament', t_code=f'{t_year}-{t_id}'))
        else:
            flash('Erros no formulário!')
            return render_template('tournament_new.html', active='tournaments', errors=errors)
    return render_template('tournament_new.html', active='tournaments', errors={})


@app.route('/admin/torneios/remover/<t_code>/')
def delete_tournament(t_code):
    _t = t_code.split('-')
    if len(_t) != 2:
        abort(400)
    t_year, t_id = _t
    tournament = read_tournament(t_id, t_year)
    if not tournament:
        abort(404)
    remove_tournament(t_id, t_year)
    flash(f"Torneio {tournament['t_name']} {tournament['tournament_year']} removido!", 'success')
    return redirect(url_for('view_tournaments'))


@app.route('/admin/torneios/limpar/<t_code>/')
def clear_tournament(t_code):
    _t = t_code.split('-')
    if len(_t) != 2:
        abort(400)
    t_year, t_id = _t
    tournament = read_tournament(t_id, t_year)
    if not tournament:
        abort(404)
    clear_tournament_matches(t_id, t_year)
    flash(f"Removidas partidas do torneio {tournament['t_name']} {tournament['tournament_year']}", 'success')
    return redirect(url_for('view_tournament', t_code=t_code))


@app.route('/admin/torneios/alterar/<t_code>/', methods=['GET', 'POST'])
def edit_tournament(t_code):
    _t = t_code.split('-')
    if len(_t) != 2:
        abort(400)
    t_year, t_id = _t
    tournament = read_tournament(t_id, t_year)
    if not tournament:
        abort(404)
    matches = read_matches_from_tournament(t_id, t_year)
    if request.method == 'GET':
        return render_template('tournament_edit.html', t=tournament, errors={}, matches=matches)
    if request.method == 'POST':
        errors = {}
        REQ = 'Campo obrigatório'
        old_id = t_id
        old_year = t_year
        t_id = request.form.get('t-id')
        if not t_id:
            errors['t-id'] = REQ
        t_id = t_id.replace('-', '_')
        t_year = request.form.get('t-year')
        if not t_year:
            errors['t-year'] = REQ
        else:
            try:
                int(t_year)
            except ValueError:
                errors['t-year'] = 'Valor inválido'
        if t_id and t_year:
            tournament = read_tournament(t_id, t_year)
            if tournament and not (old_id == t_id and int(old_year) == int(t_year)):
                errors['t-id'] = 'Em uso'
                errors['t-year'] = 'Em uso'
        t_name = request.form.get('t-name')
        if not t_name:
            errors['t-name'] = REQ
        t_date = request.form.get('t-date')
        if not t_date:
            errors['t-date'] = REQ
        if len(errors) == 0:
            update_tournament(old_id, old_year, t_id, t_year, t_name, request.form['cat'], t_date, request.form['surface'])
            flash('Torneio atualizado!', 'success')
            return redirect(url_for('view_tournament', t_code=f'{t_year}-{t_id}'))
        else:
            flash('Erros no formulário!')
            return render_template('tournament_edit.html', t=tournament, errors=errors, matches=matches)


@app.route('/admin/torneios/')
def dump_tournaments():
    page = request.args.get('page') or 1
    page = int(page)
    tournaments = read_tournaments_all(page=page)
    previous, _next = get_next_prev_links('dump_tournaments', page, tournaments, LIMIT)
    return render_template('tournaments_list.html', tournaments=tournaments, previous=previous, next=_next)


@app.route('/admin/partidas/novo/', methods=['GET', 'POST'])
def new_match():
    errors = {}
    form_tid = request.args.get('t_id')
    form_tyear = request.args.get('t_year')
    form_tname = request.args.get('t_name')
    t_names = read_tournament_names_id()
    if request.method == 'POST':
        REQ = 'Campo necessário'
        t_id = request.form.get('t-id')
        if not t_id:
            errors['t-id'] = REQ
        t_year = request.form.get('t-year')
        try:
            t_year = int(t_year)
        except ValueError:
            errors['t-year'] = 'Ano inválido'
        if len(errors) == 0 and t_year <= 1900:
            errors['t-year'] = 'Ano inválido'
        score = request.form.get('score')
        if not score:
            errors['score'] = REQ
        best_of = request.form.get('bestof')
        if not best_of:
            errors['bestof'] = REQ
        t_round = request.form.get('t-round')
        if not t_round:
            errors['t-round'] = REQ
        winner_id = request.form.get('winner-id')
        if not winner_id:
            errors['winner-id'] = REQ
        loser_id = request.form.get('loser-id')
        if not loser_id:
            errors['loser-id'] = REQ
        if len(errors) == 0:
            tournament = read_tournament(t_id, t_year)
            if not tournament:
                errors['t-id'] = 'Torneio inexistente'
                errors['t-year'] = 'Torneio inexistente'
        if len(errors) == 0:
            winner = read_player(winner_id)
            if not winner:
                errors['winner-id'] = 'Tenista não encontrado'
            loser = read_player(winner_id)
            if not loser:
                errors['loser-id'] = 'Tenista não encontrado'
            if winner_id == loser_id:
                message = 'Jogador não pode o próprio adversário'
                errors['winner-id'] = message
                errors['loser-id'] = message
        print(request.form)
        if len(errors) == 0:
            last_n = read_last_t_match(t_id, t_year)
            if last_n:
                match_number = int(last_n['match_number']) + 1
            else:
                match_number = 1
            create_match(match_number, t_id, t_year, winner_id, loser_id, score, best_of, t_round,
                         request.form.get('w-ace'), request.form.get('w-df'), request.form.get('w-svpt'), request.form.get('w-1stin'), request.form.get('w-1stwon'), request.form.get('w-2ndwon'), request.form.get('w-svgms'), request.form.get('w-bpsaved'), request.form.get('w-bpfaced'),
                         request.form.get('l-ace'), request.form.get('l-df'), request.form.get('l-svpt'), request.form.get('l-1stin'), request.form.get('l-1stwon'), request.form.get('l-2ndwon'), request.form.get('l-svgms'), request.form.get('l-bpsaved'), request.form.get('l-bpfaced'))
            flash('Partida adicionada!', 'success')
            return redirect(url_for('view_match', m_code=f'{match_number}-{t_id}-{t_year}', player_id=winner_id))
        else:
            flash('Erros no formulário!', 'error')
            return render_template('match_new.html', active='matches', errors=errors, t_names=t_names)
    return render_template('match_new.html', active='matches', errors=errors,
                           t_names=t_names, t_id=form_tid, t_year=form_tyear, t_name=form_tname)


@app.route('/admin/partidas/remover/<m_code>/', methods=['GET', 'POST'])
def delete_match(m_code):
    _m = m_code.split('-')
    if len(_m) != 3:
        abort(400)
    match_number, t_id, t_year = _m
    match = read_match(match_number, t_id, t_year)
    if not match:
        abort(404)
    remove_match(match_number, t_id, t_year)
    flash(f'Partida {m_code} removida!', 'success')
    return redirect(url_for('view_tournament', t_code=f'{t_year}-{t_id}'))


@app.route('/admin/partidas/alterar/<m_code>/', methods=['GET', 'POST'])
def edit_match(m_code):
    _m = m_code.split('-')
    if len(_m) != 3:
        abort(400)
    match_number, t_id, t_year = _m
    match = read_match(match_number, t_id, t_year)
    if not match:
        abort(404)
    old_mn, old_tid, old_tyear = match_number, t_id, t_year
    errors = {}
    t_names = read_tournament_names_id()
    if request.method == 'POST':
        REQ = 'Campo necessário'
        match_number = request.form.get('match-number')
        if not match_number:
            errors['match-number'] = REQ
        try:
            match_number = int(match_number)
        except ValueError:
            errors['match-number'] = 'Número inválido'
        t_id = request.form.get('t-id')
        if not t_id:
            errors['t-id'] = REQ
        t_year = request.form.get('t-year')
        try:
            t_year = int(t_year)
        except ValueError:
            errors['t-year'] = 'Ano inválido'
        if len(errors) == 0 and t_year <= 1900:
            errors['t-year'] = 'Ano inválido'
        score = request.form.get('score')
        if not score:
            errors['score'] = REQ
        best_of = request.form.get('bestof')
        if not best_of:
            errors['bestof'] = REQ
        t_round = request.form.get('t-round')
        if not t_round:
            errors['t-round'] = REQ
        winner_id = request.form.get('winner-id')
        if not winner_id:
            errors['winner-id'] = REQ
        loser_id = request.form.get('loser-id')
        if not loser_id:
            errors['loser-id'] = REQ
        if len(errors) == 0:
            tournament = read_tournament(t_id, t_year)
            if not tournament:
                errors['t-id'] = 'Torneio inexistente'
                errors['t-year'] = 'Torneio inexistente'
        if len(errors) == 0:
            match = read_match(match_number, t_id, t_year)
            change_id = (int(old_mn), old_tid, int(old_tyear)) != (int(match_number), t_id, int(t_year))
            if match and change_id:
                errors['match-number'] = 'Em uso'
        if len(errors) == 0:
            winner = read_player(winner_id)
            if not winner:
                errors['winner-id'] = 'Tenista não encontrado'
            loser = read_player(loser_id)
            if not loser:
                errors['loser-id'] = 'Tenista não encontrado'
            if winner_id == loser_id:
                message = 'Jogador não pode ser seu próprio adversário'
                errors['winner-id'] = message
                errors['loser-id'] = message
        if len(errors) == 0:
            update_match(match_number, t_id, t_year, winner_id, loser_id, score, best_of, t_round,
                         request.form.get('w-ace'), request.form.get('w-df'), request.form.get('w-svpt'), request.form.get('w-1stin'), request.form.get('w-1stwon'), request.form.get('w-2ndwon'), request.form.get('w-svgms'), request.form.get('w-bpsaved'), request.form.get('w-bpfaced'),
                         request.form.get('l-ace'), request.form.get('l-df'), request.form.get('l-svpt'), request.form.get('l-1stin'), request.form.get('l-1stwon'), request.form.get('l-2ndwon'), request.form.get('l-svgms'), request.form.get('l-bpsaved'), request.form.get('l-bpfaced'),
                         old_mn, old_tid, old_tyear)
            flash('Partida adicionada!', 'success')
            if change_id:
                flash('ID da partida alterado', 'warning')
            return redirect(url_for('view_match', m_code=f'{match_number}-{t_id}-{t_year}', player_id=winner_id))
        else:
            flash('Erros no formulário!', 'error')
            print(errors)
            return render_template('match_edit.html', match=match, errors=errors, active='matches', t_names=t_names)
    return render_template('match_edit.html', match=match, errors=errors, active='matches', t_names=t_names)


@app.route('/admin/partidas/')
def admin_view_matches():
    page = request.args.get('page') or 1
    page = int(page)
    player = request.args.get('tenista') or None
    t_code = request.args.get('torneio') or None
    if t_code:
        _t = t_code.split('-')
        if len(_t) != 2:
            abort(400)
        t_year, t_id = _t
    if player and t_code:
        matches = read_matches_from_player(page=page)
        previous, _next = get_next_prev_links('admin_view_matches', page, matches, LIMIT)
        return render_template('matches_list.html', matches=matches, active='matches', page=page, previous=previous, next=_next)
    if player:
        matches = read_matches_from_player(player, page=page)
        if len(matches) == 0:
            abort(404)
        else:
            previous, _next = get_next_prev_links('admin_view_matches', page, matches, LIMIT)
            return render_template('matches_list.html', matches=matches, active='matches', page=page, previous=previous, next=_next)
    if t_code:
        matches = read_matches(page=page)
        previous, _next = get_next_prev_links('admin_view_matches', page, matches, LIMIT)
        return render_template('matches_list.html', matches=matches, active='matches', page=page, previous=previous, next=_next)
    matches = read_matches(page=page)
    previous, _next = get_next_prev_links('admin_view_matches', page, matches, LIMIT)
    return render_template('matches_list.html', matches=matches, active='matches', page=page, previous=previous, next=_next)
