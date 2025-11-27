"""Generate SQL INSERTs for the osu!-style schema (countries, players, gamemodes, beatmaps, plays, etc.).
This script enforces uniqueness and referential integrity for the generated data so it can be
imported into MySQL without PRIMARY/UNIQUE key collisions.

Usage:
    py faker_osu_data.py
Produces: majer_osu_demo_data.sql (in the same folder)
"""
from faker import Faker
import random
import os
import sys
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)

# Config
NUM_COUNTRIES = 30
NUM_PLAYERS = 200
NUM_BEATMAPSETS = 150
NUM_BEATMAPS = 450
NUM_MODS = 12
NUM_PLAYS = 1200
NUM_MEDALS = 8

# Helpers

def random_date(start_years=5):
    start = datetime.now() - timedelta(days=365 * start_years)
    end = datetime.now()
    return fake.date_between(start_date=start, end_date=end).strftime('%Y-%m-%d')


def random_datetime(start_years=3):
    start = datetime.now() - timedelta(days=365 * start_years)
    end = datetime.now()
    return fake.date_time_between(start_date=start, end_date=end).strftime('%Y-%m-%d %H:%M:%S')


def sql_val(v):
    if v is None:
        return 'NULL'
    if isinstance(v, bool):
        return 'TRUE' if v else 'FALSE'
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


sql_lines = []


def insert_lines(table, columns, rows):
    sql_lines.append(f"-- {table}")
    cols = ', '.join(columns)
    for r in rows:
        vals = ', '.join(sql_val(v) for v in r)
        sql_lines.append(f"INSERT INTO {table} ({cols}) VALUES ({vals});")
    sql_lines.append("")


# 1) Countries
countries = []  # list of (code, name, flag_url)
try:
    import pycountry
    seen_codes = set()
    seen_names = set()
    for c in pycountry.countries:
        if not hasattr(c, 'alpha_2'):
            continue
        code = c.alpha_2.upper()
        name = getattr(c, 'name', code)
        if code in seen_codes or name in seen_names:
            continue
        seen_codes.add(code)
        seen_names.add(name)
        countries.append((code, name, f'https://flags.example/{code.lower()}.png'))
        if len(countries) >= NUM_COUNTRIES:
            break
    # If pycountry gave too few entries, fall back to generator
    if len(countries) < NUM_COUNTRIES:
        raise RuntimeError('pycountry did not provide enough unique countries')
except Exception:
    import re
    seen_codes = set()
    seen_names = set()
    while len(countries) < NUM_COUNTRIES:
        name = fake.unique.country()
        # derive 2-letter code from name letters
        letters = re.sub(r'[^A-Za-z]', '', name)
        if len(letters) < 2:
            base = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
        else:
            base = letters[:2].upper()
        code = base
        suffix = 0
        while code in seen_codes:
            suffix += 1
            if len(base) >= 2 and suffix < 26:
                code = base[0] + chr(((ord(base[1]) - 65 + suffix) % 26) + 65)
            else:
                code = base[0] + random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        seen_codes.add(code)
        seen_names.add(name)
        countries.append((code, name, f'https://flags.example/{code.lower()}.png'))

# Validation: ensure unique codes and names
codes = [c[0] for c in countries]
if len(codes) != len(set(codes)):
    print('ERROR: Duplicate country codes generated', file=sys.stderr)
    sys.exit(1)
names = [c[1] for c in countries]
if len(names) != len(set(names)):
    print('ERROR: Duplicate country names generated', file=sys.stderr)
    sys.exit(1)

# 2) GameModes (enum)
modes_list = ['taiko', 'standard', 'mania', 'ctb']
game_modes = [(i + 1, name, f'{name} mode') for i, name in enumerate(modes_list)]

# 3) Mods (unique code & name)
common_mods = [
    ('NF', 'No Fail', 'Player will not fail'),
    ('EZ', 'Easy', 'Reduces difficulty'),
    ('HD', 'Hidden', 'No approach circles'),
    ('HR', 'HardRock', 'Increases difficulty'),
    ('DT', 'DoubleTime', 'Faster playback'),
    ('HT', 'HalfTime', 'Slower playback'),
    ('FL', 'Flashlight', 'Limited vision'),
    ('SO', 'SpunOut', 'Spinners auto-complete'),
    ('NC', 'Nightcore', 'Special DoubleTime'),
    ('PF', 'Perfect', 'Auto-perfect'),
    ('SD', 'SuddenDeath', 'Player will fail on a miss'),
    ('TD', 'Target', 'Example mod')
]
mods = []
seen_codes = set()
seen_names = set()
for i, (code, name, desc) in enumerate(common_mods, start=1):
    if len(mods) >= NUM_MODS:
        break
    if code in seen_codes or name in seen_names:
        continue
    seen_codes.add(code)
    seen_names.add(name)
    mods.append((i, code, name, desc))
# supplement if needed
next_id = len(mods) + 1
while len(mods) < NUM_MODS:
    code = f'M{next_id:02d}'
    name = f'Mod{next_id}'
    mods.append((next_id, code, name, 'Generated mod'))
    next_id += 1

# 4) Medals
medals = []
medal_names = set()
mid = 1
while len(medals) < NUM_MEDALS:
    name = fake.unique.word().capitalize() + ' Medal'
    if name in medal_names:
        continue
    medal_names.add(name)
    medals.append((mid, name, fake.sentence(nb_words=6), f'https://medals.example/{mid}.png'))
    mid += 1

# 5) Players (username/email unique, country_code references countries)
players = []  # (id_player, username, password_hash, email, country_code, join_date)
usernames = set()
emails = set()
for pid in range(1, NUM_PLAYERS + 1):
    username = fake.unique.user_name()
    # ensure uniqueness
    if username in usernames:
        username = username + str(pid)
    usernames.add(username)

    email = fake.unique.email()
    if email in emails:
        email = f'{username}@{fake.free_email_domain()}'
    emails.add(email)

    password_hash = fake.sha256()
    country_code = random.choice(countries)[0]
    join_date = random_date(start_years=6)
    players.append((pid, username, password_hash, email, country_code, join_date))

# 6) BeatmapSets (creator uses player username)
statuses = ['Ranked', 'Loved', 'Pending', 'Graveyard']
beatmap_sets = []  # (id_set, title, artist, creator, source, tags, status, approved_date)
for sid in range(1, NUM_BEATMAPSETS + 1):
    title = fake.sentence(nb_words=3).replace('.', '')
    artist = fake.name()
    creator = random.choice(players)[1]
    source = fake.word()
    tags = ' '.join(fake.words(nb=5))
    status = random.choice(statuses)
    approved_date = None
    if status in ('Ranked', 'Loved'):
        approved_date = random_date(start_years=5)
    beatmap_sets.append((sid, title, artist, creator, source, tags, status, approved_date))

# 7) Beatmaps
beatmaps = []  # (id_beatmap, id_set, id_mode, difficulty_name, difficulty_rating, total_length, bpm, max_combo, approach_rate, overall_difficulty, circle_size, health_points)
for bid in range(1, NUM_BEATMAPS + 1):
    set_ref = random.choice(beatmap_sets)[0]
    mode_ref = random.choice(game_modes)[0]
    diff_name = fake.word().capitalize()
    diff_rating = round(random.uniform(0.5, 7.0), 2)
    total_length = random.randint(30, 600)
    bpm = random.randint(60, 220)
    max_combo = random.randint(50, 4000)
    approach_rate = round(random.uniform(0.0, 11.0), 1)
    overall_difficulty = round(random.uniform(0.0, 11.0), 1)
    circle_size = round(random.uniform(1.0, 10.0), 1)
    health_points = round(random.uniform(0.0, 10.0), 1)
    beatmaps.append((bid, set_ref, mode_ref, diff_name, diff_rating, total_length, bpm, max_combo, approach_rate, overall_difficulty, circle_size, health_points))

# 8) Plays
ranks = ['SS', 'SSH', 'S', 'SH', 'A', 'B', 'C', 'D']
plays = []  # (id_play, id_player, id_beatmap, score, max_combo, accuracy, rank, date_played, perfect)
for pid in range(1, NUM_PLAYS + 1):
    player_ref = random.choice(players)[0]
    beatmap_ref = random.choice(beatmaps)[0]
    score = random.randint(1000, 1000000)
    max_c = random.randint(1, 5000)
    accuracy = round(random.uniform(50.0, 100.0), 2)
    rank = random.choice(ranks)
    date_played = random_datetime(start_years=2)
    perfect = random.random() < 0.02
    plays.append((pid, player_ref, beatmap_ref, score, max_c, accuracy, rank, date_played, perfect))

# 9) PlayMods
playmods = []  # (id_play, id_mod)
for p in plays:
    # choose up to 3 mods per play
    k = random.randint(0, min(3, len(mods)))
    if k == 0:
        continue
    assigned = random.sample(mods, k=k)
    for m in assigned:
        playmods.append((p[0], m[0]))

# 10) PlayerMedals (unique composite key)
player_medals = []  # (id_player, id_medal, achieved_date)
seen_pm = set()
for player in players:
    n = random.randint(0, 3)
    for m in random.sample(medals, k=min(n, len(medals))):
        key = (player[0], m[0])
        if key in seen_pm:
            continue
        seen_pm.add(key)
        achieved = random_date(start_years=4)
        player_medals.append((player[0], m[0], achieved))

# 11) PlayerStats (one row per player per mode)
player_stats = []  # (id_player, id_mode, global_rank, local_rank, pp_total, playcount, overall_accuracy)
for player in players:
    for mode in game_modes:
        global_rank = random.randint(1, 50000)
        local_rank = random.randint(1, 5000)
        pp_total = round(random.uniform(0.0, 10000.0), 2)
        playcount = random.randint(0, 10000)
        overall_accuracy = round(random.uniform(0.0, 100.0), 2)
        player_stats.append((player[0], mode[0], global_rank, local_rank, pp_total, playcount, overall_accuracy))

# Final validations to avoid PRIMARY/UNIQUE collisions before writing SQL
# Countries codes & names
if len({c[0] for c in countries}) != len(countries):
    print('Duplicate country codes detected; aborting', file=sys.stderr)
    sys.exit(1)
if len({c[1] for c in countries}) != len(countries):
    print('Duplicate country names detected; aborting', file=sys.stderr)
    sys.exit(1)
# Players username/email
if len({p[1] for p in players}) != len(players):
    print('Duplicate player usernames detected; aborting', file=sys.stderr)
    sys.exit(1)
if len({p[3] for p in players}) != len(players):
    print('Duplicate player emails detected; aborting', file=sys.stderr)
    sys.exit(1)
# Mods uniqueness
if len({m[1] for m in mods}) != len(mods):
    print('Duplicate mod codes detected; aborting', file=sys.stderr)
    sys.exit(1)
if len({m[2] for m in mods}) != len(mods):
    print('Duplicate mod names detected; aborting', file=sys.stderr)
    sys.exit(1)
# Medals uniqueness
if len({m[1] for m in medals}) != len(medals):
    print('Duplicate medal names detected; aborting', file=sys.stderr)
    sys.exit(1)

# Write SQL in dependency order
insert_lines('Countries', ['code', 'name', 'flag_url'], countries)
insert_lines('GameModes', ['id_mode', 'name', 'description'], game_modes)
insert_lines('Mods', ['id_mod', 'code', 'name', 'description'], mods)
insert_lines('Medals', ['id_medal', 'name', 'description', 'icon_url'], medals)
insert_lines('Players', ['id_player', 'username', 'password_hash', 'email', 'country_code', 'join_date'], players)
insert_lines('BeatmapSets', ['id_set', 'title', 'artist', 'creator', 'source', 'tags', 'status', 'approved_date'], beatmap_sets)
insert_lines('Beatmaps', ['id_beatmap', 'id_set', 'id_mode', 'difficulty_name', 'difficulty_rating', 'total_length', 'bpm', 'max_combo', 'approach_rate', 'overall_difficulty', 'circle_size', 'health_points'], beatmaps)
insert_lines('Plays', ['id_play', 'id_player', 'id_beatmap', 'score', 'max_combo', 'accuracy', 'rank', 'date_played', 'perfect'], plays)
insert_lines('PlayMods', ['id_play', 'id_mod'], playmods)
insert_lines('PlayerMedals', ['id_player', 'id_medal', 'achieved_date'], player_medals)
insert_lines('PlayerStats', ['id_player', 'id_mode', 'global_rank', 'local_rank', 'pp_total', 'playcount', 'overall_accuracy'], player_stats)

sql_dump_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'majer_osu_demo_data.sql'))
try:
    with open(sql_dump_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql_lines))
    print(f'Wrote {len(sql_lines)} SQL lines to: {sql_dump_path}')
except Exception as e:
    print(f'ERROR writing SQL file: {e}')
