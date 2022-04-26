import time
import pandas as pd
import tkinter as tk
import logging
from bitmex import get_contracts as get_bitmex_contracts



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
    root = tk.Tk()
    root.configure(bg="gray12") #set background color

    place_currency_pair_labels(bitmex_contracts, 5)
    
   

    root.mainloop()