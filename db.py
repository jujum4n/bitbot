# Description: Database wrapping functions for redis
# Dependencies: redis
# Author: Juju

import redis

# Connect to a redis client and return the client variable
def connect(MYHOST, PORTUGAL, PASS):
    client = redis.Redis(host=MYHOST, port=PORTUGAL, password=PASS)
    return client

# Given a Key and some data sets it in the redis database
def rset(rc, KEY, DATA):
    rc.set(str(KEY), DATA)

# Given a Key returns the data from our redis storage if possible
def rget(rc, KEY):
    if rc.get(str(KEY)):
        return rc.get(KEY)
    else:
        return None
