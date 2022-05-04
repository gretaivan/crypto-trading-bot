import logging
import requests
import json
import typing

#https://www.bitmex.com/app/apiOverview
#https://www.bitmex.com/api/explorer/

logger = logging.getLogger()

class BitmexFutures:
  def __init__(self, testnet: bool):

    self._base_url = 'https://www.bitmex.com/api/v1'
    if testnet:
      self._apiKey = requests.get(self._base_url + '/apiKey')

    logger.info("Bitmex Futures Client successfully initialized")


  def _make_request(self, method: str, endpoint: str, data: typing.Dict):
    if method == "GET":
      try:
        res = requests.get(self._base_url + endpoint, params=data)
      except Exception as e:
        logger.error()
        return None

    else:
      raise ValueError()

    if res.status_code == 200:
      return res.json()
    else:
      logger.error("Error while making %s request to %s: %s (error code %s)", method, self._base_url + endpoint, res.json(), res.status_code)
      return None


  def get_contracts(self):
    endpoint = '/instrument/active'
    data = dict()

    exchange_info = self._make_request("GET", endpoint, data)

    contracts = []
    for contract in exchange_info:
      contracts.append(contract['symbol'])

    return contracts

#bitmex = BitmexClient(..., ..., ...)


"""

· place_order()

· get_balances()

· get_order_status()

· cancel_order()

· get_historical_candles()



· _generate_signature()

· _start_ws()

· _on_open(), _on_close(), _on_error, _on_message()

· _subscribe_channel()
"""