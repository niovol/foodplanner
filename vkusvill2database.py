import re

import pandas as pd

from data import compute_data_dict, load_json, save_json

xls = pd.ExcelFile("D:/YandexDisk/food/sr28abxl/ABBREV.xlsx")
base_df = xls.parse(0, index=False).drop(
    ["NDB_No", "GmWt_1", "GmWt_Desc1", "GmWt_2", "GmWt_Desc2", "Refuse_Pct"], axis=1
)
base_df.set_index("Shrt_Desc", inplace=True)
base_df.fillna(0, inplace=True)

categories_can_be_excluded = [
    "Готовая еда",
    "Сладости и десерты",
    "Супермаркет",
    "Горячая еда",
    "Роллы",
    "Веганское, растительное, постное",
    "Мясная гастрономия",
    "Чай и кофе",
    "Замороженные продукты + Айс",
    "Мороженое",
    "Хлеб и выпечка",
    "Выпекаем сами",
]

vkusvill_dict = {
    "CEREALS,OATS,INST,FORT,PLN,DRY": {
        "required_words": [r"\bгеркулес\b"],
        "optional_words": [],
    },
    "PEAS,GRN,SPLIT,MATURE SEEDS,RAW": {
        "required_words": [r"\bгорох\b", r"\bколотый\b"],
        "optional_words": [],
    },
    "PASTA,DRY,ENR": {"required_words": [r"\bмакарон"], "optional_words": []},
    "WHEAT FLOUR,WHOLE-GRAIN": {
        "required_words": [r"\bмука\b", r"\bпшеничная\b", r"\bцельнозерновая\b"],
        "optional_words": [],
    },
    "WHEAT FLR,WHITE,ALL-PURPOSE,UNENR": {
        "required_words": [r"\bмука\b", r"\bпшеничная\b"],
        "optional_words": [],
    },
    "EGG,WHL,RAW,FRSH": {"required_words": [r"\bяйцо\b"], "optional_words": []},
    "KEFIR,LOWFAT,PLN,LIFEWAY": {
        "required_words": [r"\bкефир\b"],
        "optional_words": [],
    },
    "BUCKWHEAT": {"required_words": [r"\bкрупа гречневая\b"], "optional_words": []},
    "POTATOES,FLESH & SKN,RAW": {
        "required_words": [r"\bкартофель\b"],
        "optional_words": [],
    },
    "CARROTS,RAW": {
        "required_words": [r"\bморковь\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "PARSLEY,FRSH": {
        "required_words": [r"\bпетрушка\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "DILL WEED,FRSH": {
        "required_words": [r"\bукроп\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "WATERMELON,RAW": {
        "required_words": [r"\bарбуз\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "LETTUCE,GRN LEAF,RAW": {
        "required_words": [r"\bсалат\b", r"\bлистовой\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "RICE,BROWN,LONG-GRAIN,RAW": {
        "required_words": [r"\bрис\b", r"\bбурый\b"],
        "optional_words": [],
    },
    "SPICES,BASIL,DRIED": {
        "required_words": [r"\bбазилик\b", r"\bсушен\b"],
        "optional_words": [],
    },
    "BASIL,FRESH": {
        "required_words": [r"\bбазилик\b", r"\bрп\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "PEPPERS,SWT,RED,RAW": {
        "required_words": [r"\bперец красный\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "SPINACH,RAW": {
        "required_words": [r"\bшпинат\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "AVOCADOS,RAW,CALIFORNIA": {
        "required_words": [r"\bавокадо\b"],
        "optional_words": [],
    },
    "SPICES,OREGANO,DRIED": {"required_words": [r"\bорегано\b"], "optional_words": []},
    "BROCCOLI,RAW": {"required_words": [r"\bброкколи\b"], "optional_words": []},
    "BEANS,PINK,MATURE SEEDS,RAW": {
        "required_words": [r"\bфасоль\b", r"\bкрасная\b"],
        "optional_words": [],
    },
    "BEANS,WHITE,MATURE SEEDS,CND": {
        "required_words": [r"\bфасоль\b", r"\bбелая\b"],
        "optional_words": [],
    },
    "PEAS,GRN,CND,NO SALT,SOL&LIQUIDS": {
        "required_words": [r"\bгорошек\b"],
        "optional_words": [],
    },
    "CELERY,RAW": {
        "required_words": [r"\bсельдерей\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "MILK,WHL,3.25% MILKFAT,WO/ ADDED VIT A & VITAMIN D": {
        "required_words": [r"\bмолоко\b"],
        "optional_words": [],
    },
    "RICE,WHITE,LONG-GRAIN,REG,RAW,UNENR": {
        "required_words": [r"\bрис\b", r"\bшлифованный\b", r"\bдлиннозерный\b"],
        "optional_words": [],
    },
    "WALNUTS,ENGLISH": {
        "required_words": [r"\bгрецкий\b", r"\bорех\b"],
        "optional_words": [],
    },
    "MUSHROOMS,WHITE,RAW": {"required_words": [r"\bгрибы\b"], "optional_words": []},
    "ONIONS,RAW": {
        "required_words": [r"\bлук\b", r"\bрепчатый\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "ONIONS,YOUNG GRN,TOPS ONLY": {
        "required_words": [r"\bлук\b", r"\bзеленый\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "BEANS,SNAP,GRN,FRZ,ALL STYLES,UNPREP": {
        "required_words": [r"\bфасоль\b", r"\bстручковая\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "ARUGULA,RAW": {
        "required_words": [r"\bруккола\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "ORANGES,RAW,ALL COMM VAR": {
        "required_words": [r"\bапельсины\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "BANANAS,RAW": {"required_words": [r"\bбананы\b"], "optional_words": []},
    "APPLES,RAW,WITH SKIN": {
        "required_words": [r"\bяблоко\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "GRAPEFRUIT,RAW,PINK&RED&WHITE,ALL AREAS": {
        "required_words": [r"\bгрейпфрут\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "CHEESE,COTTAGE,LOWFAT,1% MILKFAT": {
        "required_words": [r"\bтворог\b"],
        "optional_words": [],
    },
    "ALMONDS": {"required_words": [r"\bминдаль\b"], "optional_words": []},
    "CHICKEN,BROILER OR FRYERS,BRST,SKINLESS,BNLESS,MEAT ONLY,RAW": {
        "required_words": [r"\bфиле\b", r"\bгрудки\b", r"\bцыпленка\b"],
        "optional_words": [],
    },
    "CUCUMBER,WITH PEEL,RAW": {
        "required_words": [r"\bогурцы\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "PEARS,RAW": {
        "required_words": [r"\bгруша\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "THYME,FRSH": {
        "required_words": [r"\bтимьян\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "SALMON,ATLANTIC,FARMED,RAW": {
        "required_words": [r"\bсемга\b", r"\bстейк\b"],
        "optional_words": [],
    },
    "FISH,COD,PACIFIC,CKD,DRY HEAT (MAYBE PREVIOUSLY FROZEN)": {
        "required_words": [r"\треска\b"],
        "optional_words": [],
    },
    "CREAM,FLUID,HALF AND HALF": {
        "required_words": [r"\bсливки\b"],
        "optional_words": [],
    },
    "NUTS,PINE NUTS,DRIED": {
        "required_words": [r"\bкедровый\b", r"\bорех\b"],
        "optional_words": [],
    },
    "YOGURT,GREEK,PLN,WHL MILK": {
        "required_words": [r"\bйогурт\b", r"\bгреческий\b"],
        "optional_words": [],
    },
    "STRAWBERRIES,RAW": {
        "required_words": [r"\bклубника\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "BLACKBERRIES,RAW": {
        "required_words": [r"\bежевика\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "RASPBERRIES,RAW": {
        "required_words": [r"\bмалина\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "GRAPES,RED OR GRN (EURO TYPE,SUCH AS THOMPSON SEEDLESS),RAW": {
        "required_words": [r"\bвиноград\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "BLUEBERRIES,RAW": {
        "required_words": [r"\bголубика\b"],
        "optional_words": [],
        "vegetable_fruit": True,
    },
    "OIL,SUNFLOWER,HI OLEIC (70% & OVER)": {
        "required_words": [r"\bмасло\b", r"\bподсолнечное\b"],
        "optional_words": [],
    },
    "OIL,OLIVE,SALAD OR COOKING": {
        "required_words": [r"\bмасло\b", r"\bоливковое\b"],
        "optional_words": [],
    },
}


def product_nutrients(name):
    # line = df.loc[df['Shrt_Desc'] == name]
    # return line.reset_index(drop=True).drop('Shrt_Desc', axis=1).to_dict('index')[0]
    return base_df[base_df.index == name].to_dict("index")[name]


def vkusvill_nutrients(name):
    name_lower = name.lower()
    for engl, dict2 in vkusvill_dict.items():
        required_fits = all(
            re.search(word, name_lower) for word in dict2["required_words"]
        )
        optional_fits = any(
            re.search(word, name_lower) for word in dict2["optional_words"]
        )
        if required_fits and (not dict2["optional_words"] or optional_fits):
            return {"base_nutrients": product_nutrients(engl)}
    return {}


data = load_json("D:/YandexDisk/food/code/vkusvill.json")
prices_dict = {}

for good, params in data.items():
    nutrients_in_100g = params["nutrients_in_100g"]

    if (
        "Protein_(g)" in nutrients_in_100g
        or "Lipid_Tot_(g)" in nutrients_in_100g
        or "Carbohydrt_(g)" in nutrients_in_100g
    ):
        if "Protein_(g)" not in nutrients_in_100g:
            nutrients_in_100g["Protein_(g)"] = 0
        if "Lipid_Tot_(g)" not in nutrients_in_100g:
            nutrients_in_100g["Lipid_Tot_(g)"] = 0
        if "Carbohydrt_(g)" not in nutrients_in_100g:
            nutrients_in_100g["Carbohydrt_(g)"] = 0
        if "Energ_Kcal" not in nutrients_in_100g:
            nutrients_in_100g["Energ_Kcal"] = round(
                4 * nutrients_in_100g["Protein_(g)"]
                + 9 * nutrients_in_100g["Lipid_Tot_(g)"]
                + 4 * nutrients_in_100g["Carbohydrt_(g)"],
                2,
            )

    if params["category"] not in categories_can_be_excluded:
        base_params = vkusvill_nutrients(good)
        if "base_nutrients" in base_params:
            for key, value in base_params["base_nutrients"].items():
                if key not in nutrients_in_100g:
                    nutrients_in_100g[key] = value

    vegetables_fruits = 0
    if params["category"] == "Овощи, фрукты, ягоды, зелень":
        vegetables_fruits = 100
    nutrients_in_100g["vegetables_fruits"] = vegetables_fruits

    params["nutrients_total"] = {}
    if params["weight"]:
        for nutrient in nutrients_in_100g:
            params["nutrients_total"][nutrient] = round(
                nutrients_in_100g[nutrient] * params["weight"] / 100, 2
            )
    if "price" in params:
        price = params["price"]
        if "value" in price and "unit" in price:
            if "шт" in price["unit"]:
                price["item"] = price["value"]
                if params["weight"]:
                    price["kg"] = round(price["value"] / params["weight"] * 1000, 2)
                    price["100g"] = round(price["value"] / params["weight"] * 100, 2)
            elif "кг" in price["unit"]:
                price["kg"] = price["value"]
                price["100g"] = price["value"] / 10

            if "100g" in price and params["category"] not in categories_can_be_excluded:
                if "base_nutrients" in base_params:
                    prices_dict[good] = price["100g"]

    if "Energ_Kcal" in params["nutrients_in_100g"]:
        kcal = params["nutrients_in_100g"]["Energ_Kcal"]
        if kcal > 0.0:
            params["nutrients_in_kcal"] = {}
            for nutrient in nutrients_in_100g:
                params["nutrients_in_kcal"][nutrient] = round(
                    params["nutrients_in_100g"][nutrient] / kcal, 5
                )

    if "100g" in params["price"]:
        params["nutrients_in_rouble"] = {}
        for nutrient in nutrients_in_100g:
            price = params["price"]["100g"]
            params["nutrients_in_rouble"][nutrient] = round(
                params["nutrients_in_100g"][nutrient] / price, 5
            )

dishes = load_json("D:/YandexDisk/food/code/dishes.json")

data.update(compute_data_dict(dishes, data))

save_json("D:/YandexDisk/food/code/food_database.json", data)
save_json("D:/YandexDisk/food/code/prices.json", prices_dict)
