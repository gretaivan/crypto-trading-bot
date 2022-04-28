import time
from numpy import load
import pandas as pd
import tkinter as tk
import logging
from connectors.bitmex import get_contracts as get_bitmex_contracts
from connectors.binance_futures import BinanceFutures
import os
from dotenv import load_dotenv

load_dotenv()
#unix timestamp since 1970
#print(time.time())

logger = logging.getLogger()
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

def place_currency_pair_labels(contracts, rows_per_column): 
    i = 0 #row 
    j = 0 #column 

    calibri_font= ("Calibri", 11, "normal")

    for contract in contracts: 
        label_widget = tk.Label(root, text=contract, bg='gray12', fg='SteelBlue1', width=13, font=calibri_font)
        label_widget.grid(row=i,  column=j, sticky='ew') #sticky sticks on the east and west
        
        if i == (rows_per_column-1): 
            j += 1
            i = 0
        else: 
            i+= 1 



if __name__ == '__main__':

    bitmex_contracts = get_bitmex_contracts()
 
    print(os.getenv('PUBLIC_KEY'))

    binance = BinanceFutures(os.getenv('PUBLIC_KEY'), os.getenv('SECRET_KEY'),  True)
    # print(binance.get_balances())
    # print(binance.place_order("BTCUSDT", "BUY", 0.01, "LIMIT", 20000, "GTC")) # good till cancelled
    # print(binance.get_order_status("BTCUSDT", 3036361555))
    # print(binance.cancel_order("BTCUSDT", 3036361555))
    

    root = tk.Tk()
    root.configure(bg="gray12") #set background color

    #bitmex simple version
    place_currency_pair_labels(bitmex_contracts, 5)
    
    #binance 

    root.mainloop()