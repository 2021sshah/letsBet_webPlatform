import class_file as cf
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
 
game1 = cf.game("NFL", "sea", datetime.datetime.now()- datetime.timedelta(days=6))
game1.get_data()
 
 
bet_line1 = cf.bet_line(game1, False)
bet_line1.set_metric("First Downs")
bet_line1.set_metric_amount(20)
bet_line1.set_bet_choice()
print(bet_line1, bet_line1.find_hit())
 
 
bet_line2 = cf.bet_line(game1, False)
bet_line2.set_metric("First Downs")
bet_line2.set_metric_amount(18)
bet_line2.set_bet_choice()
print(bet_line2, bet_line2.find_hit())
 
 
bet_line3 = cf.bet_line(game1, True)
bet_line3.set_metric('Passing Cmp')
bet_line3.set_metric_amount(70)
bet_line3.set_bet_choice("Kyler Murray")
print(bet_line3, bet_line3.find_hit())
 
bet_line4 = cf.bet_line(game1, True)
bet_line4.set_metric('Passing Cmp')
bet_line4.set_metric_amount(20)
bet_line4.set_bet_choice("Kyler Murray")
print(bet_line4, bet_line4.find_hit())
 
bet_line5 = cf.bet_line(game1, True)
bet_line5.set_metric('Passing TD')
bet_line5.set_metric_amount(.5)
bet_line5.set_bet_choice("Geno Smith")
bet_line5.make_spread("Kyler Murray")
print(bet_line5, bet_line5.find_hit())