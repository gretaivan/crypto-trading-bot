from concurrent.futures import thread
import logging
import re
import requests
import pprint
import time
import hmac
import hashlib
from urllib.parse import urlencode  # parsing to url query
import websocket
import threading 
import json 

logger = logging.getLogger()

# streams url 

class BinanceFutures:
	def __init__(self, public_key, secret_key, testnet):  #self is a class constructor to initialise self when called and testnet whic api to use
		if testnet: 
			self.base_url = "https://testnet.binancefuture.com"
			self.wss_url = "wss://stream.binance.com/ws" 
		else: 
			self.base_url = "https://fapi.binance.com"
			self.wss_url = "wss://fstream.binance.com/ws" 

		#communication identity vars
		self.public_key = public_key
		self.secret_key = secret_key
		self.headers = {'X-MBX-APIKEY': self.public_key}

		self.prices = dict()
		self.id = 1
		self.ws  = None

		#as this is a websocket function and it runs continuosly it requires its own thread to run in parallel
		t = threading.Thread(target=self.start_ws)
		t.start()

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

	def start_ws(self):
		self.ws = websocket.WebSocketApp(self.wss_url, on_open=self.on_open, on_close=self.on_close, on_error=self.on_error, on_message=self.on_message)
		self.ws.run_forever()
		return

	def on_open(self, ws):
		logger.info("Binance Websocket connection opened")
		self.subscribe_channel("BTCUSDT")

	def on_close(self, ws):
		logger.warning("Binance Websocket connection closed")

	def on_error(self, ws, msg):
		logger.warning("Binance Websocket connection: %s", msg)

	def on_message(self, ws, msg):
	
		data = json.loads(msg)

		if "e" in data is not None: 
			if data['e'] == "bookTicker":
				symbol = data['s']
				
				if symbol not in self.prices: 
					self.prices[symbol] = {'bid': float(data['b']), 'ask': float(data['a'])}
			else: 
				self.prices[symbol]['bid'] = float(data['b'])
				self.prices[symbol]['ask'] = float(data['a'])

			print(self.prices[symbol])

	def subscribe_channel(self, symbol): 
		data = dict()
		data['method'] = 'SUBSCRIBE'
		data['params'] = []
		# bookTicker give price updates
		data['params'].append(symbol.lower() + "@bookTicker")
		data['id'] = self.id 
		
		"""
		data example
		2022-04-28 16:37:01,656 INFO :: Binance Websocket: {"u":18790914162,"s":"BTCUSDT","b":"39590.41000000","B":"2.08454000","a":"39590.42000000","A":"1.99151000"}
		"""
		self.ws.send(json.dumps(data))
		self.id += 1 


	
	
		