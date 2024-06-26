import json


def load_json(file_path):
    with open(file_path, encoding="utf-8") as json_file:
        return json.load(json_file)


def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)


def compute_data_dict(compounds, data):
    new_data = {}
    for name, composition in compounds.items():
        new_data[name] = {
            "category": "Блюдо",
            "price": {"item": 0, "kg": 0, "100g": 0},
            "weight": 0,
            "nutrients_in_100g": {},
            "nutrients_total": {},
        }
        for item, weight in composition.items():
            new_data[name]["weight"] += weight
            if item in data:
                item_data = data[item]
                new_data[name]["price"]["item"] += (
                    item_data["price"]["100g"] / 100 * weight
                )
                for nutrient, amount in item_data["nutrients_in_100g"].items():
                    if nutrient not in new_data[name]["nutrients_total"]:
                        new_data[name]["nutrients_total"][nutrient] = 0
                    new_data[name]["nutrients_total"][nutrient] += amount / 100 * weight

        new_data[name] = _calculate_nutrient_ratios(new_data[name])
    return new_data


def _calculate_nutrient_ratios(dish_data):
    weight = dish_data["weight"]
    price = dish_data["price"]
    for nutrient, amount in dish_data["nutrients_total"].items():
        dish_data["nutrients_in_100g"][nutrient] = round(amount / weight * 100, 2)
        dish_data["nutrients_total"][nutrient] = round(amount, 2)
    price["kg"] = round(price["item"] / weight * 1000, 2)
    price["100g"] = round(price["item"] / weight * 100, 2)
    return dish_data
