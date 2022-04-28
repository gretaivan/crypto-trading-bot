class Candle:
    def __init__(self, data):
        self.timestamp = data[0]
        self.open = float(data[1])
        self.high = float(data[2])
        self.low = float(data[3])
        self.close = float(data[4])
        self.volume = float(data[5])
