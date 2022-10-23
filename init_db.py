import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor() # allows _____ method calls

# user
cur.execute("INSERT INTO users (fullname, username, passwrd, wallet) VALUES (?, ?, ?, ?)",
            ('John Doe', 'sample_user', 'password', 500) )

# placed_bets
cur.execute("INSERT INTO placed_bets (league, game_date, team_name, player, bet_type, metric, "
            "metric_amount, hit_pool, miss_pool) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('NFL', '23/10/2022', 'ATL', 'None', 'spread', 'Points', '10', '200', '150') )

# cur.execute("INSERT INTO placed_bets (title, content) VALUES (?, ?)",
#             ('Second Post', 'Content for the second post') )

# comments
cur.execute("INSERT INTO comments (bet_id, content) VALUES(?, ?)",
            (1, 'Sample comment for 1st bet') )

cur.execute("INSERT INTO comments (bet_id, content) VALUES(?, ?)",
            (1, 'Sample reply for 1st bet') )

cur.execute("INSERT INTO comments (bet_id, content) VALUES(?, ?)",
            (2, 'Sample comment for 2st bet') )

connection.commit()
connection.close()