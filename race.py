# Description: Contains information related to the racing functions
# Dependencies: discord.py and Python 3.5 along with Ubuntu
# Author: Juju
from random import randint
import time
racers = []
race_going = False
all_carts = ['🚎','🚗','🚕','🚙','🚌','🏍' ,'🏎','🚐','🚜','🚂','🚁','🚲']
checkered_flag = '🏁'
carts_used = []


def get_rand_cart():
    t = randint(0, len(all_carts))
    return t

# Class to hold all of our race information
class Race:
    def __init__(self, initiate, cart=None):
        self.initiate = initiate
        race_initiate = Racer(initiate, cart)
        self.racers = [race_initiate]
        self.places = []
    def stop_race(self):
        self.started = False
        self.finished = False
    def start_race(self):
        self.started = True
        self.finished = True
    
    # Adds a racer to the racers list    
    def add_racer(self, racer):
        self.racers.append(racer)
    
    def move_racer(self, racer):
        if not racer.finished:
            movement = randint(1, 10)
            if movement + racer.percentage > 100:
                racer.percentage = 100
                racer.finished = True
                racer.race_display = checkered_flag + racer.cart + ' - ' + racer.name
            racer.percentage += movement
            if (racer.percentage > 100):
                racer.percentage = 100
            racer.race_display = checkered_flag +' ' + '.' * (100 - racer.percentage) + racer.cart + ' ' + racer.name +' - ' + str(racer.percentage)+'%'
    
      
class Racer:
    def __init__(self, name, cart):
        self.name = name
        self.percentage = 0
        self.finished = False
        self.race_dist = '.' * (100 - self.percentage)
        self.cart = ''
        self.place = 0
        if cart and cart in all_carts:
            self.cart = cart
        else:
            self.cart = get_rand_cart()

        self.race_display = checkered_flag + self.race_dist + self.cart + ' ' + self.name + ' - '+ str(self.percentage)+'%'
        
        self.race_finished = checkered_flag + ' ' +self.cart + ' ' + self.name + ' - ' + str(self.place)
