# Crypto Currency Trading Bot in Python

Windows desktop app for crypto portfolio management - using REST API and live data streams. User can place, cancel order, overview status and balance of the their account and see live market data. It is a multithreaded application

## Tools

- Python 3.7.9
- numpy-1.21.2
- pandas-1.3.3
- python-dateutil-2.8.2
- pytz-2021.1 six-1.16
- numpy
- python-dateutil
- python-dotenv
- requests
- websocket-client v0.58.0

## Installation & Usage

### Installation

- `pipenv --python 3.7.9` - to setup project with required python version
- `pipenv shell` - enter virtual env
- `pipenv install pandas numpy python-dateutil pytz requests --dev` - install required dependencies
- `pipenv requirements --dev > requirements.txt` - generate the requirement list

### Usage

- `pipenv shell` - enter VE
- `python main.py` - to run application

## App Planning

### Requirements

#### 1. Interface

- [ ] Display market data (decision helper)
- [ ] Display messages to the user (loggin)
- [ ] Set up a strategy and start/stop it
- [ ] Follow the orders/trades (PNL, order status...)  
       _(4 components)_

###### Interface design version 1.0

![image](https://user-images.githubusercontent.com/47504179/132955706-689fcb33-f217-4981-b26a-c453a8cf3f54.png)

#### 2. Connectivity (APIs)

- [x] Binance futures API
- [ ] Bitmex API
- [ ] Authentication to both APIs  
       Using 2 types of connections REST API and web socket API
      _(2 connectors)_

#### 3. Trading Automation

- [ ] Parse parameters set by the user in the interface
- [ ] Parse market data received by connectors
- [ ] Define a logic for each strategy (entry and exit)
- [ ] Manage orders / positions
      _(Strategy class)_

#### 4. Other

- [x] Multi-threading: to enable live data updates in paraller to user interactions
- [ ] Logger to log actions in the dedicated file

### Desktop vs Web App

This application is developed for the desktop use to avoid number of security issues related to the web applications. As well as avoid the need of high compute power when deployed, thus reduce the cost. The main goal of this app is to explore the principles and strategies of trading applications and related algorithms, as well as utilise the existing APIs for crypto trading.

| Desktop                                                         | Web App                                       |
| --------------------------------------------------------------- | --------------------------------------------- |
| **Pros**                                                        |
|                                                                 |
| Easier to handle security                                       | Strict separation of front and back end       |
| Easier to develop                                               | Interface design is superior                  |
| Uses local computing power                                      | Easier to make it available to multiple users |
| Can run on the server as well                                   | Accessible through any device                 |
|                                                                 |
| **Cons**                                                        |
|                                                                 |
| Interface design is limited                                     | Needs to handle authentication                |
| Needs to be installed on every machine                          | Expensive and consumes a lot of compute power |
| Needs a separate development to handle different operational OS |
