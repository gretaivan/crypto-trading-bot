import logging
import requests
import pprint

logger = logging.getLogger()


"https://testnet.binancefuture.com"
"wss://fstream.binance.com" 

def get_contracts(): 
  # get base endpoint for futures
  response_object = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
  #print(response_object.status_code, response_object.json())
  #pprint.pprint(response_object.json()['symbols'])
  """ AVAILABLE CURRENCY PAIRS """
  contracts = []
  for contract in response_object.json()['symbols']:
    #pprint.pprint(contract['pair'])
    contracts.append(contract['pair'])
  
  return contracts
