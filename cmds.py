import urllib
import json
import os
import subprocess
from random import randint
from urllib.parse import quote_plus
import urllib.request
import requests
from utils import get_token

bing_token = get_token('bing')
giphy_token = get_token('giphy')
# Format of token: filename: name.token, filecontent = {"token":"tokenvalue"}

def bing_search(query):
    # Your base API URL; change "Image" to "Web" for web results.
    url = "https://api.datamarket.azure.com/Bing/Search/v1/Image"

    # Query parameters. Don't try using urlencode here.
    # Don't ask why, but Bing needs the "$" in front of its parameters.
    # The '$top' parameter limits the number of search results.
    url += "?$format=json&$top=1&Query=%27{}%27".format(quote_plus(query))
    
    # You can get your primary account key at https://datamarket.azure.com/account
    r = requests.get(url, auth=("", bing_token))
    resp = json.loads(r.text)
    return(resp)

def get_qod():
    url = 'http://quotes.rest/qod.json'
    response = urllib.request.urlopen(url)
    data = response.read()      # a `bytes` object
    text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
    data = json.loads(text)
    qod = data['contents']['quotes'][0]['quote'] + ' - ' + data['contents']['quotes'][0]['author']
    return qod

def get_xkcd():
    url = 'https://xkcd.com/info.0.json'
    response = urllib.request.urlopen(url)
    data = response.read()      # a `bytes` object
    text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
    data = json.loads(text)
    return data['img']    
    
def get_giphy_trending():
    url = 'https://api.giphy.com/v1/gifs/trending?api_key='+ giphy_token + '&limit=1&fmt=json'
    response = urllib.request.urlopen(url)
    data = response.read()      # a `bytes` object
    text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
    data = json.loads(text)
    urlfront = 'http://i.giphy.com/' + str(data['data'][0]['id'])+ '.gif'
    return urlfront

def get_btc_price():
    response = urllib.request.urlopen("https://coinbase.com/api/v1/prices/spot_rate?currency=USD")
    data = response.read()      # a `bytes` object
    text = data.decode('utf-8') # a `str`; this step can't be used if data is binary
    data = json.loads(text)
    return str('1 BTC = ' + data['amount']+' USD')
 
    
def flip():
    rand_num = randint(0,1)
    if rand_num == 0:
        return 'Heads'
    if rand_num == 1:
        return 'Tails'