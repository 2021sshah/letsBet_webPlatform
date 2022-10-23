import pandas as pd
import datetime
import datetime
import pandas as pd
import numpy as np
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer
import time as t
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
 
def NFL_parse(soup):
    team_stats = soup.find("table", id = "team_stats")
 
    col_names = [i.text for i in team_stats.find_all("th")]
   
    team1 = col_names[1]
    team2 = col_names[2]
    col_names = col_names[3:]
   
    stats = [i.text for i in team_stats.find_all("td")]
   
    grouping = [[stats[i], stats[i +1]] for i in range(0, len(stats), 2)]
   
    df = pd.DataFrame(grouping, col_names, columns = [team1, team2])
   
    team1_CAYTI = df[team1]["Cmp-Att-Yd-TD-INT"].split("-")
    team2_CAYTI = df[team2]["Cmp-Att-Yd-TD-INT"].split("-")
    df2 = pd.DataFrame(list(zip(team1_CAYTI, team2_CAYTI)), ["Pass Cmp", "Pass Att", "Pass Yards", "Pass TD", "INT"], columns = [team1, team2])
   
    team1_RYT = df[team1]["Rush-Yds-TDs"].split("-")
    team2_RYT = df[team2]["Rush-Yds-TDs"].split("-")
    df3 = pd.DataFrame(list(zip(team1_RYT, team2_RYT)), ["Rush Attempts", "Rush Yards", "Rush TD"], columns = [team1, team2])
   
    df4 = pd.DataFrame(list(zip(df[team1]["Sacked-Yards"].split("-"), df[team2]["Sacked-Yards"].split("-"))), ["Sacks", "Sack Yards"], columns = [team1, team2])
    df5 = pd.DataFrame(list(zip(df[team1]["Fumbles-Lost"].split("-"), df[team2]["Fumbles-Lost"].split("-"))), ["Fumbles", "Fumbles Lost"], columns = [team1, team2])
    df6 = pd.DataFrame(list(zip(df[team1]["Penalties-Yards"].split("-"), df[team2]["Penalties-Yards"].split("-"))), ["Penalties", "Penalty Yards"], columns = [team1, team2])
   
    team_df_final = pd.concat([df, df2, df3, df4, df5])
    team_df_final = team_df_final.drop(labels=["Rush-Yds-TDs","Cmp-Att-Yd-TD-INT", "Fumbles-Lost", "Sacked-Yards", "Penalties-Yards"], axis=0)
    #add total td and total points
   
 
 
    #offensive players
    player_offense = soup.find("table", id = "player_offense")
   
    cat_names = [i.text for i in player_offense.find_all("th")][6:15] #not name
    cat_names += [i.text for i in player_offense.find_all("th")][16:27]
   
    for i in range(1,9): cat_names[i] = "Passing " + cat_names[i]
    for i in range(9,13): cat_names[i] = "Rushing " + cat_names[i]
    for i in range(13,18): cat_names[i] = "Receiving " + cat_names[i]
   
    offense_names = [i.text for i in player_offense.find_all("a")]
   
    player_stats = [i.text for i in player_offense.find_all("td")]
    player_stats_grouped = []
    for i in range(0,len(player_stats),21):
        player_stats_grouped.append(player_stats[i:i+21])
   
    for i in range(len(player_stats_grouped)):
        player_stats_grouped[i].pop(9)
   
    off_df = pd.DataFrame(player_stats_grouped, offense_names, columns = cat_names)
 
    #defensive players
    player_defense = soup.find("table", id = "player_defense")
   
    cat_names = [i.text for i in player_defense.find_all("th")][6:22] #not name
    for i in range(1,6): cat_names[i] = "Interceptions " + cat_names[i]
    for i in range(7,12): cat_names[i] = "Tackles " + cat_names[i]
    for i in range(12,len(cat_names)): cat_names[i] = "Fumbles " + cat_names[i]
   
    defense_names = [i.text for i in player_defense.find_all("a")]
   
    player_stats = [i.text for i in player_defense.find_all("td")]
    player_stats_grouped = []
    for i in range(0,len(player_stats),16):
        player_stats_grouped.append(player_stats[i:i+16])
   
    def_df = pd.DataFrame(player_stats_grouped, defense_names, columns = cat_names)
 
    return team_df_final, off_df, def_df
 
# object for a game
class game:
     def __init__(self, league, team, date):
        self.league = league
        self.team = team
        self.date = date
 
     def __str__(self):
         return "GAME INFO-> League: {}  Team: {}  Date: {}".format(self.league, self.team, self.date)
 
 
     #returns bool if the game has started  
     def game_started(self):
         if self.date < datetime.datetime.now():
            return True
         else:
            return False
 
 
    #returns bool if the game is over  
     def game_over(self):
         if self.date + datetime.timedelta(days=.5) < datetime.datetime.now():
            return True
         else:
            return False
 
     def get_data(self):
        if self.game_over() == True:
            date = self.date.strftime("%y%m%d")
            print(date)
            if self.league == "NBA":
                sport = 'basketball'
            elif self.league == "NFL":
                sport = 'football'
 
            driver = webdriver.Firefox()
            driver.get("https://www.pro-{}-reference.com/boxscores/20{}0{}.htm".format(sport, date, self.team))
            team_df_final, off_df, def_df = NFL_parse(BeautifulSoup(driver.page_source))
 
            self.team_df = team_df_final
 
            for i in self.team_df.columns:
                if i != self.team.upper():
                    self.opp_team = i
 
           
            self.off_df = off_df
            self.def_df = def_df
 
 
 
 
 
# object for individual betting line
class bet_line:
    def __init__(self, game, player):
        self.over_under = True
        self.game = game
        self.player = player
        self.bet_choice = None
        self.metric = None
        self.metric_amount = None
        self.true_metric_amount = None
 
    def __str__(self):
        if self.over_under == True:
            bet_type = "Over/Under"
 
        else:
            bet_type = "Spread"
 
        return "BET LINE-> {} {} {} {} {} {}".format(self.bet_choice, self.metric, bet_type, self.spread_against, self.metric_amount, self.game.date)
 
 
    def make_spread(self, against = None):
        if self.player == True:
            self.spread_against = against
        else:
            self.spread_against = self.game.opp_team
 
        self.over_under = False
       
 
 
 
    #returns bool if the bet has all needed info to be placed
    def bet_info_complete(self):
        if self.bet_choice != None and self.metric != None and self.metric_amount != None:
            return True
        else:
            return False
 
 
    #sets the object (player or team) of the bet
    def set_bet_choice(self, bet_choice = None):
        if self.player == False:
            self.bet_choice = self.game.team
        else:
            print("i")
            self.bet_choice = bet_choice
   
    # sets the metrics (points, assist, blocks etc) that is being bet on
    def set_metric(self, metric):
        self.metric = metric
 
    # sets the amount for that metric. Represents the spread or the over under depending on the bet
    def set_metric_amount(self, metric_amount):
        self.metric_amount = metric_amount
 
 
    # determins if the bet hit or not
    def find_hit(self):
        if self.game.game_over() == True:
 
            if self.over_under == True:
 
                if self.player == True:
 
                    if self.bet_choice in self.game.off_df.index:
                       
                        return float(self.game.off_df.loc[self.bet_choice, self.metric]) >= self.metric_amount
 
                   
                    elif self.bet_choice in self.game.def_df.index:
 
                        return float(self.game.def_df.loc[self.bet_choice, self.metric]) >= self.metric_amount
 
                else:
 
                    return float(self.game.team_df.loc[self.metric, self.game.team.upper()]) >= self.metric_amount
 
            else:
                if self.player == False:
                    return float(self.game.team_df.loc[self.metric, self.game.team.upper()]) - float(self.game.team_df.loc[self.metric, self.game.opp_team]) >= self.metric_amount
                else:
                    if self.bet_choice in self.game.off_df.index:
                       
                        print(self.game.off_df)
                        return float(self.game.off_df.loc[self.bet_choice, self.metric]) - float(self.game.off_df.loc[self.spread_against, self.metric]) >= self.metric_amount
 
                   
                    elif self.bet_choice in self.game.def_df.index:
 
                        return float(self.game.def_df.loc[self.bet_choice, self.metric]) - float(self.game.def_df.loc[self.spread_against, self.metric]) >= self.metric_amount
 
 
               
               
 
# object for an user
class user:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.wallet = 0
        self.date = None
        self.fullname = None
 
    def __str__(self):
        return "name:{} password:{} wallet: {}".format(self.username, self.password, self.wallet )
   
    # changes the amount of money that user had
    def change_wallet(self, amount):
        self.wallet += amount
       
   
 
class bet:
    def __init__(self, placed_user, all = True):
        self.placed_user = placed_user
        self.all = all
        self.needs_match = False
        self.live = False
        self.bet_list = []
 
        self.bettors = pd.DataFrame(columns = ["user", "username", "hit", "amount", "share", "payout"])
        self.hit_pool = 0
        self.miss_pool = 0
   
 
 
    # adds a line to the bet
    def add_bet_line(self, bet_line):
        self.bet_list.append(bet_line)
 
    # adds a user to the bet
    def add_user_bet(self, user_placed_by, amount, hit):
 
        self.bettors.loc[len(self.bettors.index)
                ] = [user_placed_by, user_placed_by.username, hit, amount, np.nan, np.nan]
 
 
        if hit == True:
            self.hit_pool += amount
            better_pool = self.hit_pool
            opp_pool = self.miss_pool
 
        else:
            self.miss_pool += amount
            better_pool = self.miss_pool
            opp_pool = self.hit_pool
 
 
        self.bettors["share"] = self.bettors['amount'] / better_pool
        self.bettors["payout"] = self.bettors['share'] * opp_pool
       
 
    # adds the first user to the bet
    def add_first_bet(self, amount, hit):
        self.first_hit = hit
        self.add_user_bet(self.placed_user, amount, hit)
   
    # adds the second user to the bet
    def add_match_bet(self, user_matched):
        self.add_user_bet(user_matched, self.bettors['amount'].iloc[0], not self.first_hit)
 
 
    # need to add webscraper or api
    def find_outcome(self):
        if len(self.bet_list) == 0:
            return None
 
        if self.all == True:
            for i in self.bet_list:
                if i.find_hit() == False:
                    return False
 
            return True
       
        else:
            for i in self.bet_list:
                if i.find_hit() == True:
                    return True
                   
            return False
 
   
    # sets the outcome of the bet
    def set_outcome(self):
        self.outcome = self.find_outcome()
 
 
    # runs the payout for the bet
    def payout(self):
 
        for index, row in self.bettors.iterrows():
            if row['hit'] == self.outcome:
                row['user'].change_wallet(row['payout'])
            else:
                row['user'].change_wallet(-row['amount'])
           
 


