import logging
import requests
import pprint

logger = logging.getLogger()



"wss://fstream.binance.com" 


# gets crypto currency pairs / contracts
# def get_contracts(): 
#   	response_object = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
#   	contracts = []
#   	for contract in response_object.json()['symbols']:
#     	contracts.append(contract['pair'])
  
#   	return contracts


class BinanceFutures:
	def __init__(self, testnet):  #self is a class constructor to initialise self when called and testnet whic api to use
		if testnet: 
			self.base_url = "https://testnet.binancefuture.com"
		else: 
			self.base_url = "https://fapi.binance.com

			self.prices = dict()

		logger.info("Binances Futures Client successfully initialized")

	def make_request(self, method, endpoint, data):
		if method == "GET":
			res = requests.get(self.base_url + endpoint, params=data)
		else: 
			raise ValueError()

		if res.status_code == 200: 
			return res.json()
		else: 
			logger.error("Error while making %s request to %s : %s (error code %s)", 
							method, endpoint, res.json(), res.status_code)
			return None

	def get_contracts(self): 
		exchange_info = self.make_request("GET", "fapi/v1/exchangeInfo", None)

		contracts_dictionary = dict()

		if exchange_info is not None: 
			for contract_data in exchange_info['symbols']: 
				contracts_dictionary[contract_data['pair']] = contract_data 
			
		return contracts_dictionary
	
	def get_historical_candles(self, symbol, interval): 
		endpoint = "fapi/v1/klines"
		data = dict()
		data['symbol'] = symbol
		data['interval']  = interval
		data['limit'] = 1000 

		raw_candles = self.make_request("GET", endpoint, data)

		candles = [] # will be list of lists

		if raw_candles is not None: 
			for candle in raw_candles: 
				"""
				in API candle data is a list itself consisting of: 
								0: open time, 1: Open price, 2: High, 3: Low, 4: Close, 5: Volume
				"""
				candles.append([candle[0], float(candle[1]), float(candle[2]), float(candle[3]), float(candle[4]), float(candle[5])])   

		return candles

	def get_bid_ask(self, symbol): 
		endpoint = "fapi/v1/ticker/bookTicker"
		data = dict()
		data['symbol'] = symbol
		ob_data = self.make_request("GET", endpoint, data)

		if ob_data is not None: 
			is symbol not in self.prices: 
				self.prices[symbol] = {'bid': float(ob_data['bidPrice']), 'ask': float(on_data['askPrice'])}
			else: 
				seld.prices[symbol]['bid'] = float(ob_data['bidPrice'])
				seld.prices[symbol]['ask'] = float(ob_data['askPrice'])

		return self.prices[symbol]