################################################################################
#Filename: ./mod/btc.py
#Description: Grabs the current Bitcoin spot rate from Coinbase
#Python Version: 2.7.x
#!/usr/bin/python
#Author : Justin Chase
################################################################################
import json, urllib2
 
def getprice():
    data=json.load(urllib2.urlopen("https://coinbase.com/api/v1/prices/spot_rate?currency=USD"))
    return data
 
def main():
    try:
        data = getprice()
        print '1 BTC = ' + data['amount']+' USD'
    except:
        print 'Could not acquire Bitcoin Price'
 
if __name__ == "__main__":
    main()