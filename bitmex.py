import requests
import pprint

def get_contracts(): 

  response_object = requests.get("https://www.bitmex.com/api/v1/instrument/active")

  """ AVAILABLE CURRENCY PAIRS """
  for contract in response_object.json():
    contracts = []
    pprint.pprint(contract['symbol'])
    contracts.append(contract['symbol'])
    
  return contracts

print(get_contracts())