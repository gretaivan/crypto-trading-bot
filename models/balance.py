class Balance:
    def __init__(self, data):
        self.initial_margin = float(data['initialMargin'])
        self.maintenance_margin = float(data['maintMargin'])
        self.margin_balance = float(data['marginBalance'])
        self.wallet_balance = float(data['walletBalance'])
        self.unrealised_profit = float(data['unrealisedProfit'])
