import json
import random
from functools import cmp_to_key

import numpy as np
import pandas as pd
from scipy.optimize import linprog

from data import load_json, save_json
from nutrient_ranges import calculate_nutrient_ranges


def filter_full_data_products(data):
    full_data_products = {}

    nutrient_keys = [
        "Water_(g)",
        "Energ_Kcal",
        "Protein_(g)",
        "Lipid_Tot_(g)",
        "Ash_(g)",
        "Carbohydrt_(g)",
        "Fiber_TD_(g)",
        "Sugar_Tot_(g)",
        "Calcium_(mg)",
        "Iron_(mg)",
        "Magnesium_(mg)",
        "Phosphorus_(mg)",
        "Potassium_(mg)",
        "Sodium_(mg)",
        "Zinc_(mg)",
        "Copper_mg)",
        "Manganese_(mg)",
        "Selenium_(µg)",
        "Vit_C_(mg)",
        "Thiamin_(mg)",
        "Riboflavin_(mg)",
        "Niacin_(mg)",
        "Panto_Acid_mg)",
        "Vit_B6_(mg)",
        "Folate_Tot_(µg)",
        "Folic_Acid_(µg)",
        "Food_Folate_(µg)",
        "Folate_DFE_(µg)",
        "Choline_Tot_ (mg)",
        "Vit_B12_(µg)",
        "Vit_A_IU",
        "Vit_A_RAE",
        "Retinol_(µg)",
        "Alpha_Carot_(µg)",
        "Beta_Carot_(µg)",
        "Beta_Crypt_(µg)",
        "Lycopene_(µg)",
        "Lut+Zea_ (µg)",
        "Vit_E_(mg)",
        "Vit_D_µg",
        "Vit_D_IU",
        "Vit_K_(µg)",
        "FA_Sat_(g)",
        "FA_Mono_(g)",
        "FA_Poly_(g)",
        "Cholestrl_(mg)",
        "vegetables_fruits",
    ]

    for product, product_data in data.items():
        nutrients_in_100g = product_data.get("nutrients_in_100g", {})
        if all(nutrient in nutrients_in_100g for nutrient in nutrient_keys):
            full_data_products[product] = product_data

    return full_data_products


def filter_price(data):
    filtered_data = {}

    for key, value in data.items():
        if "price" in value and "100g" in value["price"]:
            filtered_data[key] = value

    return filtered_data


# data = load_json('D:/YandexDisk/food/code/food_database.json')
data = load_json("D:/YandexDisk/food/code/opt_data.json")
filtered_data = filter_full_data_products(data)
filtered_data = filter_price(filtered_data)

nutrient_ranges = calculate_nutrient_ranges(
    gender="female",
    height=1.7,
    weight_cur=64,
    age=32,
    activity_multiplier=1.375,
    breastfeeding=True,
)


def get_optimal_diet(filtered_data, nutrient_ranges):
    product_names = list(filtered_data.keys())
    product_nutrients = [
        product["nutrients_in_100g"] for product in filtered_data.values()
    ]
    max_weights = [product["max_weight"] / 100 for product in filtered_data.values()]
    product_prices = [product["price"]["100g"] for product in filtered_data.values()]

    n_products = len(product_names)
    n_nutrients = len(product_nutrients[0])

    c = product_prices

    A_eq = np.zeros((1, n_products))
    A_eq[0, :] = [nutrients_dict["Energ_Kcal"] for nutrients_dict in product_nutrients]
    b_eq = np.array([nutrient_ranges["Energ_Kcal"][2]])

    A_ub = []
    b_ub = []

    for nutrient, values in nutrient_ranges.items():
        if nutrient != "Energ_Kcal":
            min_value = values[1]
            optimal_value = values[2]
            max_value = values[4]

            lower_bound_row = np.zeros(n_products)
            upper_bound_row = np.zeros(n_products)

            for i in range(n_products):
                if nutrient in product_nutrients[i]:
                    lower_bound_row[i] = -product_nutrients[i][nutrient]
                    upper_bound_row[i] = product_nutrients[i][nutrient]

            A_ub.append(lower_bound_row)
            A_ub.append(upper_bound_row)
            b_ub.append(-min_value)
            b_ub.append(max_value)

    for i in range(n_products):
        weight_constraint_row = np.zeros(n_products)
        weight_constraint_row[i] = 1
        A_ub.append(weight_constraint_row)
        b_ub.append(max_weights[i])

    A_ub = np.array(A_ub)
    b_ub = np.array(b_ub)

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, method="highs")

    if not result.success:
        return "not success"

    product_weights = result.x * 100
    optimal_diet = {}

    for i in range(n_products):
        if product_weights[i] > 1e-6:
            optimal_diet[product_names[i]] = product_weights[i]

    return optimal_diet


optimal_diet = get_optimal_diet(filtered_data, nutrient_ranges)
print(optimal_diet)
