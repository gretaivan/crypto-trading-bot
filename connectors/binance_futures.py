import logging
import re
import requests
import pprint
import time
import hmac
import hashlib
from urllib.parse import urlencode

logger = logging.getLogger()

# streams url "wss://fstream.binance.com" 

class BinanceFutures:
	def __init__(self, public_key, secret_key, testnet):  #self is a class constructor to initialise self when called and testnet whic api to use
		if testnet: 
			self.base_url = "https://testnet.binancefuture.com"
		else: 
			self.base_url = "https://fapi.binance.com"

		#communication identity vars
		self.public_key = public_key
		self.secret_key = secret_key
		self.headers = {'X-MBX-APIKEY': self.public_key}

		self.prices = dict()

		logger.info("Binances Futures Client successfully initialized")

	def generate_signature(self, data): 

		return hmac.new(self.secret_key.encode(), urlencode(data).encode(), hashlib.sha256).hexdigest()  #byte type is created with .encode()


	def make_request(self, method, endpoint, data):
		if method == "GET": 
			res = requests.get(self.base_url + endpoint, params=data, headers=self.headers)
		elif method == "POST": 
			res = requests.post(self.base_url + endpoint, params=data, headers=self.headers)
		elif method == "DELETE": 
			res = requests.delete(self.base_url + endpoint, params=data, headers=self.headers)
		else: 
			raise ValueError()

		if res.status_code == 200: 
			return res.json()
		else: 
			logger.error("Error while making %s request to %s : %s (error code %s)", 
							method, endpoint, res.json(), res.status_code)
			return None

	def get_contracts(self): 
		exchange_info = self.make_request("GET", "/fapi/v1/exchangeInfo", None)

		contracts_dictionary = dict()

		if exchange_info is not None: 
			for contract_data in exchange_info['symbols']: 
				contracts_dictionary[contract_data['pair']] = contract_data 
			
		return contracts_dictionary
	
	def get_historical_candles(self, symbol, interval): 
		endpoint = "/fapi/v1/klines"
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
		endpoint = "/fapi/v1/ticker/bookTicker"
		data = dict()
		data['symbol'] = symbol
		ob_data = self.make_request("GET", endpoint, data)

		if ob_data is not None: 
			if symbol not in self.prices: 
				self.prices[symbol] = {'bid': float(ob_data['bidPrice']), 'ask': float(ob_data['askPrice'])}
			else: 
				self.prices[symbol]['bid'] = float(ob_data['bidPrice'])
				self.prices[symbol]['ask'] = float(ob_data['askPrice'])

		return self.prices[symbol]

	def get_balances(self): 
		data = dict()
		data['timestamp'] = int(time.time() * 1000)  #API requires ms as int
		data['signature']  = self.generate_signature(data)
		endpoint = "/fapi/v1/account"
		
		balances = dict()

		account_data = self.make_request("GET", endpoint, data)

		if account_data is not None: 
			for asset in account_data['assets']:
				balances[asset['asset']] = asset
		
		return balances
	
	def place_order(self, symbol, side, quantity, order_type, price=None, tif=None): 
		data = dict()
		data['symbol'] = symbol
		data['side'] = side 
		data['quantity'] = quantity
		data['type'] = order_type
		if price is not None: 
			data['price'] = price
		if tif is not None: 
			data['timeInForce'] = tif 
		data['timestamp'] = int(time.time() * 1000)
		data['signature'] = self.generate_signature(data)

		endpoint = '/fapi/v1/order'
		order_status = self.make_request("POST", endpoint, data)
		
		return order_status

	def cancel_order(self, symbol, order_id): 
		data = dict()
		data['orderId'] = order_id
		data['symbol'] = symbol
		data['timestamp'] = int(time.time() * 1000)
		data['signature'] = self.generate_signature(data)

		endpoint = '/fapi/v1/order'
		order_status = self.make_request("DELETE", endpoint, data)

		return order_status

	def get_order_status(self, symbol, order_id): 
		data = dict()
		data['symbol'] = symbol 
		data['orderId'] = order_id
		data['timestamp'] = int(time.time() * 1000)
		data['signature'] = self.generate_signature(data)

		endpoint = "/fapi/v1/order"

		order_status = self.make_request("GET", endpoint, data)
		return order_status