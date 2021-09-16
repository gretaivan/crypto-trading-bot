# Crypto Currency Trading Bot in Python 
Windows desktop app

## Tools
+ Python 3 

## App Planning

### Requirements
#### 1. Interface
- [ ] Display market data (decision helper)
- [ ] Display messages to the user (loggin)
- [ ] Set up a strategy and start/stop it
- [ ] Follow the orders/trades (PNL, order status...)  
*(4 components)*

###### Interface design version 1.0
![image](https://user-images.githubusercontent.com/47504179/132955706-689fcb33-f217-4981-b26a-c453a8cf3f54.png)

#### 2. Conenctivity (APIs) 
- [ ] Binance futures API 
- [ ] Bitmex API
- [ ] Authentication to both APIs  
*(2 connectors)*

#### 3. Trading Automation
- [ ] Parse parameters set by the user in the interface
- [ ] Parse market data received by connectors
- [ ] Define a logic for each strategy (entry and exit)
- [ ] Manage orders / positions
*(Strategy class)*




### Desktop vs Web App
This application is developed for the desktop use to avoid number of security issues related to the web applications. As well as avoid the need of high compute power when deployed, thus reduce the cost. The main goal of this app is to explore the principles and strategies of trading applications and related algorithms, as well as utilise the existing APIs for crypto trading. 

| Desktop | Web App|
| ------ | ----- |
| **Pros**| 
||
|Easier to handle security| Strict separation of front and back end|
|Easier to develop | Interface design is superior |
|Uses local computing power| Easier to make it available to multiple users|
|Can run on the server as well| Accessible through any device|
||
| **Cons** |
||
| Interface design is limited| Needs to handle authentication |
| Needs to be installed on every machine| Expensive and consumes a lot of compute power |
| Needs a separate development to handle different operational OS | 
