# Description: Utility functions
# Dependencies: NA
# Author: Juju

import datetime
import json

# Generic Helper function that just tries to print any data, p is shorter than print
def p(DATA):
    print(DATA)

# Grabs our bots token from a file called cert.token
def get_token(name):
    with open(name+'.token') as json_data:
        d = json.load(json_data)
        return d['token']

def msg(DATA):
    toprint = str(str(datetime.datetime.now()) + ': ' + DATA)
    p(toprint)
