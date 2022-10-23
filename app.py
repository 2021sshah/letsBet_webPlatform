from unicodedata import category
from flask import Flask, render_template, request, url_for, flash, redirect
import sqlite3
from werkzeug.exceptions import abort
import class_file as cf


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# GLOBAL USER STATUS
logged_in = False
user_obj = cf.user()


def get_db_connection():
   conn = sqlite3.connect('database.db')
   conn.row_factory = sqlite3.Row
   return conn


@app.route('/',  methods=('GET', 'POST'))
def index():
	conn = get_db_connection()
	placed_bets = conn.execute('SELECT * FROM placed_bets').fetchall()
	
	if request.method == 'POST':
		filter_player = request.form['player_name']
		filter_team = request.form['team_name']
		
		if filter_player:
			filtered_bets = conn.execute('SELECT * FROM placed_bets WHERE player = ?',(filter_player,)).fetchall()
		elif filter_team :
			filtered_bets = conn.execute('SELECT * FROM placed_bets WHERE team_name = ?',(filter_team,)).fetchall()
		else:
			filtered_bets = conn.execute('SELECT * FROM placed_bets').fetchall()

		placed_bets = filtered_bets
			
	conn.close()
	return render_template('index.html', placed_bets=placed_bets)


def get_placed_bet(bet_id):
   conn = get_db_connection()
   placed_bet = conn.execute('SELECT * FROM placed_bets WHERE id = ?',
					(bet_id,)).fetchone()
   involved = conn.execute('SELECT * FROM involved WHERE bet_id = ?',
				   (bet_id,)).fetchall()
   comments = conn.execute('SELECT * FROM comments WHERE bet_id = ?',
				   (bet_id,)).fetchall()
   conn.close()
   if placed_bet is None: abort(404)
   return placed_bet, involved, comments


@app.route('/bet<int:bet_id>', methods=('GET', 'POST'))
def bet(bet_id):
	global logged_in, user_obj
	if not logged_in: # handle edge case
		flash('Please login to view specific bet!', category='error')
		return redirect(url_for('login'))

	if request.method == 'POST':
		# bet_id in method param
		hit_miss = request.form['hit_miss']
		amount = request.form['amount']
		content = request.form['content']

		if not (hit_miss and amount) and not content:
			flash('Either complete bet or comment must be placed!', category='error')

		if hit_miss and amount:
			if not (hit_miss == 'hit' or hit_miss == 'miss'):
				flash("Pool must be either 'hit' or 'miss'", category='error')
			elif not amount.isdigit():
				flash('Please insert integer bet amount', category='error')
			elif int(amount) > user_obj.wallet:
				flash('ERROR! Cannot bet over wallet balance', category='error')
			else:
				# Handle adding to pool and involved
				bet_amount = int(amount)
				conn = get_db_connection()

				conn.execute('INSERT INTO involved (username, bet_id, hit_miss, bet_amount) '
								'VALUES (?, ?, ?, ?)',
								(user_obj.username, bet_id, hit_miss, bet_amount))
				placed_bet = conn.execute('SELECT * FROM placed_bets WHERE id = ?',
								(bet_id,)).fetchone()
				if hit_miss == 'hit':
					conn.execute('UPDATE placed_bets SET hit_pool = ? WHERE id = ?', 
							('{}'.format(bet_amount + int(placed_bet['hit_pool'])), bet_id))
				else:
					conn.execute('UPDATE placed_bets SET miss_pool = ? WHERE id = ?', 
							('{}'.format(bet_amount + int(placed_bet['miss_pool'])), bet_id))
				# update wallet
				user_obj.wallet -= bet_amount
				conn.execute('UPDATE users SET wallet = ?'
							' WHERE username = ?', 
							('{}'.format(user_obj.wallet), user_obj.username))

				conn.commit()
				conn.close()
				flash('Successfully placed bet!', category='success')

		if content:
			conn = get_db_connection()
			conn.execute('INSERT INTO comments (bet_id, content) VALUES (?, ?)',
                     (bet_id, content))
			conn.commit()
			conn.close()
			flash('Comment successfully placed!', category='success')

	placed_bet, involved, comments = get_placed_bet(bet_id)
	return render_template('bet.html', bet=placed_bet, comments=comments, wallet=user_obj.wallet)


@app.route('/register', methods=('GET', 'POST'))
def register():
	global logged_in, user_obj
	if request.method == 'POST': # entire method

		fullname = request.form['fullname']
		username = request.form['username']
		password = request.form['password']
		wallet = request.form['wallet'] # check before int_cast from str

		conn = get_db_connection()
		usernames = conn.execute('SELECT username FROM users').fetchall() # list of all usernames
		conn.close()

		if not fullname or not username or not password or not wallet:
			flash('All input fields required!', category='error')
		elif username in usernames:
			flash('Username is already taken!', category='error')
		elif not wallet.isdigit():
			flash('Please insert an integer wallet balance', category='error')
		else:
			# update user
			logged_in = True
			user_obj.date = 'Just Now'
			user_obj.fullname = fullname
			user_obj.username = username
			user_obj.password = password
			user_obj.wallet = int(wallet)

			conn = get_db_connection()
			conn.execute('INSERT INTO users (fullname, username, passwrd, wallet) VALUES (?, ?, ?, ?)',
                     (user_obj.fullname, user_obj.username, user_obj.password, user_obj.wallet))
			conn.commit()
			conn.close()

			flash('User successfully added!', category='success')
			return redirect(url_for('account'))

	return render_template('register.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
	global logged_in, user_obj
	if logged_in: # handle edge case
		flash('Already logged in!', category='success')
		return redirect(url_for('account'))
	
	if request.method == 'POST': # entire method
		username = request.form['username']
		password = request.form['password']

		conn = get_db_connection()
		usernames = conn.execute('SELECT username FROM users').fetchall() # list of all usernames
		conn.close()
		usernames = [i['username'] for i in usernames]

		if not username or not password:
			flash('Both username and password required!', category='error')
		elif username not in usernames:
			flash('Username is not registered!', category='error')
		else:
			conn = get_db_connection()
			data = conn.execute('SELECT * FROM users WHERE username = ?',
					(username,)).fetchone() # list of all usernames
			conn.commit()
			conn.close()
			if password != data['passwrd']: # password incorrect
				flash('Incorrect password for given username! Please try again', category='error')
			else: # password correct
				logged_in = True
				create_date = data['created'].strip()
				user_obj.date = create_date[:create_date.find(' ')] # format accordingly
				user_obj.fullname = data['fullname']
				user_obj.username = data['username']
				user_obj.wallet = int(data['wallet'])
				flash('Welcome {}! Your remaining wallet balance is ${}'.format(user_obj.fullname, user_obj.wallet),
							category='success')
				return redirect(url_for('account')) # redirect account

	return render_template('login.html')
   

def get_my_bets():
   global user_obj
   conn = get_db_connection()
   user_involved = conn.execute('SELECT * FROM involved WHERE username = ?',
				   (user_obj.username,)).fetchall()
   user_proposed = conn.execute('SELECT * FROM proposed_bets WHERE username = ?',
				   (user_obj.username,)).fetchall()
   # process for user_placed
   involved_lst = [(i['bet_id'], i['hit_miss'], i['bet_amount']) for i in user_involved]
   user_placed = []
   for bet_id, hit_miss, bet_amount in involved_lst:
      bet_dct = conn.execute('SELECT * FROM placed_bets WHERE id = ?',
				(bet_id,)).fetchone()
      # manually merge sql tables
      merge_dct = {}
      merge_dct['id'] = bet_dct['id']
      merge_dct['created'] = bet_dct['created']
      merge_dct['league'] = bet_dct['league']
      merge_dct['game_date'] = bet_dct['game_date']
      merge_dct['team_name'] = bet_dct['team_name']
      merge_dct['player'] = bet_dct['player']
      merge_dct['bet_type'] = bet_dct['bet_type']
      merge_dct['metric'] = bet_dct['metric']
      merge_dct['metric_amount'] = bet_dct['metric_amount']
      merge_dct['hit_miss'] = hit_miss
      merge_dct['bet_amount'] = bet_amount
      # update user_placed
      user_placed.append(merge_dct)

   conn.close()
   return user_placed, user_proposed


@app.route('/account', methods=('GET', 'POST'))
def account():
	global logged_in, user_obj
	if not logged_in: # handle edge case
		flash('Please login first!', category='error')
		return redirect(url_for('login'))
	
	if request.method == 'POST': # entire method
		
		funds = request.form['funds']
		if not funds:
			flash('Bet amount required!', category='error')
		elif not funds.isdigit():
			flash('Please add integer additional funds', category='error')
		else:
			user_obj.wallet += int(funds)

			conn = get_db_connection() # CHECK
			conn.execute('UPDATE users SET wallet = ?'
							' WHERE username = ?', 
							('{}'.format(user_obj.wallet), user_obj.username))
			conn.commit()
			conn.close()

			flash('Success! Your new wallet balance is ${}'.format(user_obj.wallet), category='success')
			# later could modify user information

	placed_lst, proposed_lst = get_my_bets()
	return render_template('account.html', user=user_obj, placed_bets=placed_lst, proposed_bets=proposed_lst)


@app.route('/signout')
def signout():
	global logged_in, user_obj
	logged_in = False
	user_obj = cf.user()
	flash('Sign out successful!', category='success')
	return redirect(url_for('login'))


@app.route('/create', methods=('GET', 'POST'))
def create():
	global logged_in, user_obj
	if not logged_in: # handle edge case
		flash('Please login first!', category='error')
		return redirect(url_for('login'))
	
	if request.method == 'POST': # parse inputs
			league = request.form['league']
			game_date = request.form['game_date'] # str DD/MM/YYYY
			team_name = request.form['team_name']
			player = request.form['player'] # player str or ''
			bet_type = request.form['bet_type'] # str 'over/under' or 'spread'
			metric = request.form['metric']
			metric_amount = request.form['metric_amount']
			hit_miss = request.form['hit_miss']
			bet_amount = request.form['bet_amount']

			if not league or not game_date or not team_name or not bet_type or not metric or not metric_amount or not hit_miss or not bet_amount:
				flash('All inputs except player required!', category='error')
			# handle cases for incorrect bet made
			elif not (bet_type == 'over' or bet_type == 'under' or bet_type == 'spread'):
				flash("Bet type must be either 'over', 'under', or 'spread'", category='error')
			elif not metric_amount.replace('.', '', 1).isdigit():
				flash('Metric amount must be a decimal!', category='error')
			elif not (hit_miss == 'hit' or hit_miss == 'miss'):
				flash("Hit/Miss must be either 'hit' or 'miss'", category='error')
			elif not bet_amount.isdigit():
				flash('Bet amount must be an integer!', category='error')
			elif int(bet_amount) > user_obj.wallet:
				flash('Error! Cannot bet more than wallet balance', category='error')
			else:
				# modify inputs
				if not player: player = 'None'
				conn = get_db_connection()
				conn.execute('INSERT INTO proposed_bets (username, league, game_date, team_name, player, bet_type, metric, metric_amount, hit_miss, bet_amount)'
          					'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     	(user_obj.username, league, game_date, team_name, player, bet_type, metric, metric_amount, hit_miss, bet_amount))
				user_obj.wallet -= int(bet_amount)
				conn.execute('UPDATE users SET wallet = ?'
							' WHERE username = ?', 
							('{}'.format(user_obj.wallet), user_obj.username))
				conn.commit()
				conn.close()
				flash('Bet successfully proposed!', category='success')
				return redirect(url_for('account'))
		
	return render_template('create.html')


def get_proposed_bet(): # change to get bet
   conn = get_db_connection()
   proposed = conn.execute('SELECT * FROM proposed_bets').fetchall()
   conn.close()
   return proposed


@app.route('/all_proposed', methods=('GET', 'POST'))
def all_proposed():
   conn = get_db_connection()
   proposed_bets = conn.execute('SELECT * FROM proposed_bets').fetchall()
   
   if request.method == 'POST':
      filter_player = request.form['player_name']
      filter_team = request.form['team_name']
      
      if filter_player:
         filtered_bets = conn.execute('SELECT * FROM proposed_bets WHERE player = ?',(filter_player,)).fetchall()
      elif filter_team:
         filtered_bets = conn.execute('SELECT * FROM proposed_bets WHERE team_name = ?',(filter_team,)).fetchall()
      else:
         filtered_bets = conn.execute('SELECT * FROM proposed_bets').fetchall()
      
      proposed_bets = filtered_bets

   conn.close()
   return render_template('all_proposed.html', proposed_bets=proposed_bets)


@app.route('/proposed<int:prop_id>', methods=('GET', 'POST'))
def proposed(prop_id):
   global logged_in, user_obj
   if not logged_in: # handle edge case
      flash('Please login first!', category='error')
      return redirect(url_for('login'))
	
   # POST requires proposed_amount
   conn = get_db_connection()
   proposed_bet = conn.execute('SELECT * FROM proposed_bets WHERE id = ?',
					   (prop_id,)).fetchone()
   proposed_amount = int(proposed_bet['bet_amount'])
   conn.close()

   if request.method == 'POST': # Parse all inputs

      amount = request.form['amount']

      if not amount:
         flash('Bet amount required!', category='error')
      elif not amount.isdigit():
         flash('Please insert integer bet amount', category='error')
      elif int(amount) > user_obj.wallet:
         flash('ERROR! Cannot bet over wallet balance', category='error')
      elif int(amount) < proposed_amount:
         flash('ERROR! Must bet at least proposed amount', catagory='error')
      else:
         # handle adding to pool and involved
         bet_amount = int(amount)
         prop_dct = proposed_bet
         conn = get_db_connection()
         cursor = conn.cursor()

         # insert into placed_bets
         hit_pool = bet_amount if prop_dct['hit_miss'] == 'miss' else proposed_amount
         miss_pool = proposed_amount if prop_dct['hit_miss'] == 'miss' else bet_amount

         cursor.execute("INSERT INTO placed_bets (league, game_date, team_name, player, bet_type, metric, "
                     "metric_amount, hit_pool, miss_pool) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                     (prop_dct['league'], prop_dct['game_date'], prop_dct['team_name'], prop_dct['player'], 
                     prop_dct['bet_type'], prop_dct['metric'], prop_dct['metric_amount'], hit_pool, miss_pool))
         placed_id = cursor.lastrowid
         # insert into involved
         against = 'hit' if prop_dct['hit_miss'] == 'miss' else 'miss'
         conn.execute('INSERT INTO involved (username, bet_id, hit_miss, bet_amount) '
							'VALUES (?, ?, ?, ?)',
							(user_obj.username, placed_id, against, bet_amount))
         conn.execute('INSERT INTO involved (username, bet_id, hit_miss, bet_amount) '
							'VALUES (?, ?, ?, ?)',
							(prop_dct['username'], placed_id, prop_dct['hit_miss'], prop_dct['bet_amount']))
         
         # remove from proposed_bets
         conn.execute('DELETE FROM proposed_bets WHERE id = ?', (prop_id,))
         
         # update wallet
         user_obj.wallet -= bet_amount
         conn.execute('UPDATE users SET wallet = ?'
							' WHERE username = ?', 
							('{}'.format(user_obj.wallet), user_obj.username))
         
         conn.commit()
         conn.close()

         flash('Bet successfully placed!', category='success')
         return redirect(url_for('account'))

      
   return render_template('proposed.html', bet=proposed_bet, wallet=user_obj.wallet)


# Deploy Flask Locally
if __name__ == '__main__':
	app.run()