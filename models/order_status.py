class OrderStatus: 
  def __init__ (self, data): 
    self.order_id = data['orderId']
    self.status  = data['status']
    self.avg_price = float(data['avgPrice'])