import requests
import pprint

def get_contracts(): 

  response_object = requests.get("https://www.bitmex.com/api/v1/instrument/active")
  pprint.pprint(response_object.json())
  contracts = []
  """ AVAILABLE CURRENCY PAIRS """
  for contract in response_object.json():
    contracts.append(contract['symbol'])

  return contracts