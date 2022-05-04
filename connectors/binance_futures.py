import logging
import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode  # parsing to url query
import websocket
import threading
import json
import typing

from models import *

logger = logging.getLogger()


class BinanceFutures:
    def __init__(self, public_key: str, secret_key: str, testnet: bool):  # self is a class constructor to initialise self when called and testnet which api to use
        if testnet:
            self._base_url = "https://testnet.binancefuture.com"
            self._wss_url = "wss://stream.binance.com/ws"
        else:
            self._base_url = "https://fapi.binance.com"
            self._wss_url = "wss://fstream.binance.com/ws"

        # communication identity vars
        self._public_key = public_key
        self._secret_key = secret_key
        self._headers = {'X-MBX-APIKEY': self._public_key}

        self.contracts = self.get_contracts()
        self.balances = self.get_balances()
        self.prices = dict()
        self._ws_id = 1
        self._ws = None

        # as this is a websocket function and it runs continously it requires its own thread to run in parallel
        t = threading.Thread(target=self._start_ws)
        t.start()

        logger.info("Binances Futures Client successfully initialized")

    def _generate_signature(self, data: typing.Dict) -> str:

        return hmac.new(self._secret_key.encode(), urlencode(data).encode(),
                        hashlib.sha256).hexdigest()  # byte type is created with .encode()

    def _make_request(self, method: str, endpoint: str, data: typing.Dict):
        if method == "GET":
            try:
                res = requests.get(self._base_url + endpoint, params=data, headers=self._headers)
            except Exception as e:
                logger.error("Connection error while making %s request to %s: %s", method, endpoint, e)
                return None
        elif method == "POST":
            try:
                res = requests.post(self._base_url + endpoint, params=data, headers=self._headers)
            except Exception as e:
                logger.error("Connection error while making %s request to %s: %s", method, endpoint, e)
                return None
        elif method == "DELETE":
            try:
                res = requests.delete(self._base_url + endpoint, params=data, headers=self._headers)
            except Exception as e:
                logger.error("Connection error while making %s request to %s: %s", method, endpoint, e)
                return None
        else:
            raise ValueError()

        if res.status_code == 200:
            return res.json()
        else:
            logger.error("Error while making %s request to %s : %s (error code %s)", method, endpoint, res.json(),
                         res.status_code)
            return None

    def get_contracts(self) -> typing.Dict[str, Contract]:
        exchange_info = self._make_request("GET", "/fapi/v1/exchangeInfo", None)

        contracts = dict()

        if exchange_info is not None:
            for contract_data in exchange_info['symbols']:
                contracts[contract_data['pair']] = Contract(contract_data)

        return contracts

    def get_historical_candles(self, contract: Contract, interval: str) -> typing.List[Candle]:
        endpoint = "/fapi/v1/klines"
        data = dict()
        data['symbol'] = contract.symbol
        data['interval'] = interval
        data['limit'] = 1000

        raw_candles = self._make_request("GET", endpoint, data)

        candles = []  # will be list of lists

        if raw_candles is not None:
            for candle in raw_candles:
                """
				in API candle data is a list itself consisting of: 
								0: open time, 1: Open price, 2: High, 3: Low, 4: Close, 5: Volume
				"""
                candles.append(Candle(candle))

        return candles

    def get_bid_ask(self, contract: Contract) -> typing.Dict[str, float]:
        endpoint = "/fapi/v1/ticker/bookTicker"
        data = dict()
        data['symbol'] = contract.symbol
        ob_data = self._make_request("GET", endpoint, data)

        if ob_data is not None:
            if contract.symbol not in self.prices:
                self.prices[contract.symbol] = {'bid': float(ob_data['bidPrice']), 'ask': float(ob_data['askPrice'])}
            else:
                self.prices[contract.symbol]['bid'] = float(ob_data['bidPrice'])
                self.prices[contract.symbol]['ask'] = float(ob_data['askPrice'])

            return self.prices[contract.symbol]

    def get_balances(self) -> typing.Dict[str, Balance]:
        data = dict()
        data['timestamp'] = int(time.time() * 1000)  # API requires ms as int
        data['signature'] = self._generate_signature(data)
        endpoint = "/fapi/v1/account"

        balances = dict()

        account_data = self._make_request("GET", endpoint, data)

        if account_data is not None:
            for asset in account_data['assets']:
                balances[asset['asset']] = Balance(asset)

        return balances

    def place_order(self, contract: Contract, side: str, quantity: float, order_type: str, price=None, tif=None):
        data = dict()
        data['symbol'] = contract.symbol
        data['side'] = side
        data['quantity'] = quantity
        data['type'] = order_type
        if price is not None:
            data['price'] = price
        if tif is not None:
            data['timeInForce'] = tif
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        endpoint = '/fapi/v1/order'
        order_status = self._make_request("POST", endpoint, data)

        if order_status is not None:
            order_status = OrderStatus(order_status)

        return order_status

    def cancel_order(self, contract: Contract, order_id: int):
        data = dict()
        data['orderId'] = order_id
        data['symbol'] = contract.symbol
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        endpoint = '/fapi/v1/order'
        order_status = self._make_request("DELETE", endpoint, data)

        if order_status is not None:
            order_status = OrderStatus(order_status)

        return order_status

    def get_order_status(self, contract: Contract, order_id: int) -> OrderStatus:
        data = dict()
        data['symbol'] = contract.symbol
        data['orderId'] = order_id
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self._generate_signature(data)

        endpoint = "/fapi/v1/order"

        order_status = self._make_request("GET", endpoint, data)

        if order_status is not None:
            order_status = OrderStatus(order_status)

        return order_status

    def _start_ws(self):
        self._ws = websocket.WebSocketApp(self._wss_url, on_open=self._on_open, on_close=self._on_close,
                                          on_error=self._on_error, on_message=self._on_message)
        while True:
            try:
                self._ws.run_forever()
            except Exception as e:
                logger.error("Websocket error in run_forever() method: %s", e)
            time.sleep(2) # reconnect every 2sec

    def _on_open(self, ws):
        logger.info("Binance Websocket connection opened")
        self.subscribe_channel(list(self.contracts.values()), "bookTicker")

    def _on_close(self, ws):
        logger.warning("Binance Websocket connection closed")

    def _on_error(self, ws, msg: str):
        logger.warning("Binance Websocket connection: %s", msg)

    def _on_message(self, ws, msg: str):

        data = json.loads(msg)

        if "e" in data is not None:
            if data['e'] == "bookTicker":
                symbol = data['s']

                if symbol not in self.prices:
                    self.prices[symbol] = {'bid': float(data['b']), 'ask': float(data['a'])}
                else:
                    self.prices[symbol]['bid'] = float(data['b'])
                    self.prices[symbol]['ask'] = float(data['a'])

    def subscribe_channel(self, contracts: typing.List[Contract], channel: str):
        data = dict()
        data['method'] = 'SUBSCRIBE'
        data['params'] = []

        for contract in contracts:
            # bookTicker give price updates
            data['params'].append(contract.symbol.lower() + "@" + channel)

        data['id'] = self._ws_id

        """
            data example
            2022-04-28 16:37:01,656 INFO :: Binance Websocket: {"u":18790914162,"s":"BTCUSDT","b":"39590.41000000","B":"2.08454000","a":"39590.42000000","A":"1.99151000"}
		"""
        try:
            self._ws.send(json.dumps(data))
        except Exception as e:
            logger.error("Websocket error while subscribing to %s with %s items, maximum is 200: %s", channel, len(contracts), e)
        self._ws_id += 1


