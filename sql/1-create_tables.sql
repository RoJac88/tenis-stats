CREATE TABLE IF NOT EXISTS Players (
    id               INTEGER PRIMARY KEY,
    first_name       VARCHAR(50) NOT NULL,
    last_name        VARCHAR(50) NOT NULL,
    birthdate        DATE NOT NULL,
    hand             CHAR(1) NOT NULL,
    country          CHAR(3) NOT NULL,
    img              VARCHAR(255),
    height           INTEGER NULL
);

CREATE TABLE IF NOT EXISTS Tournaments (
    tournament_id          VARCHAR(64) NOT NULL,
    tournament_year        INTEGER NOT NULL,
    t_name                 VARCHAR(50) NOT NULL,
    atp_level              CHAR(1) NOT NULL,
    t_date                 DATE NOT NULL,
    surface                CHAR(1) NOT NULL,
    PRIMARY KEY (tournament_year, tournament_id),
    CONSTRAINT check_atp_level CHECK (
        atp_level = 'G' OR 
        atp_level = 'D' OR
        atp_level = 'A')
);

CREATE TABLE IF NOT EXISTS Matches (
    match_number        INTEGER NOT NULL,
    t_id                VARCHAR(64) NOT NULL,
    t_year              INTEGER NOT NULL,
    winner_id           INTEGER NOT NULL,
    loser_id            INTEGER NOT NULL,
    score               VARCHAR(32) NOT NULL,
    best_of             CHAR(1) NOT NULL,
    t_round             VARCHAR(3) NOT NULL,
    /* Stats */
    w_ace               INTEGER NULL,
    w_df                INTEGER NULL,
    w_svpt              INTEGER NULL,
    w_1stIn             INTEGER NULL,
    w_1stWon            INTEGER NULL,
    w_2ndWon            INTEGER NULL,
    w_SvGms             INTEGER NULL,
    w_bpSaved           INTEGER NULL,
    w_bpFaced           INTEGER NULL,
    l_ace               INTEGER NULL,
    l_df                INTEGER NULL,
    l_svpt              INTEGER NULL,
    l_1stIn             INTEGER NULL,
    l_1stWon            INTEGER NULL,
    l_2ndWon            INTEGER NULL,
    l_SvGms             INTEGER NULL,
    l_bpSaved           INTEGER NULL,
    l_bpFaced           INTEGER NULL,
    mins                INTEGER NULL,
    PRIMARY KEY (t_year, t_id, match_number),
    FOREIGN KEY (t_id, t_year) REFERENCES Tournaments (tournament_id, tournament_year),
    FOREIGN KEY (winner_id) REFERENCES Players (id),
    FOREIGN KEY (loser_id) REFERENCES Players (id),
    CONSTRAINT check_best_of CHECK (best_of = '3' OR best_of = '5')
);
