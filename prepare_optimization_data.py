import re

import pandas as pd

from data import compute_data_dict, load_json, save_json

prices = load_json("D:/YandexDisk/food/code/prices_corrected.json")
food_database = load_json("D:/YandexDisk/food/code/food_database.json")

opt_data = {}
for key, value in prices.items():
    if key in food_database:
        opt_data[key] = {}
        opt_data[key]["nutrients_in_100g"] = food_database[key]["nutrients_in_100g"]
        opt_data[key]["price"] = {}
        opt_data[key]["price"]["100g"] = prices[key]
save_json("D:/YandexDisk/food/code/opt_data.json", opt_data)
