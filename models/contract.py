class Contract:
    def __init__(self, data):
        self.symbol = data['symbol']
        self.base_asset = data['baseAsset']
        self.quote_asset = data['quoteAsset']
        self.price_precision = data['pricePrecision']
        self.quantity_precision = data['quantityPrecision']
