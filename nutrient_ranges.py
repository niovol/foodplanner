import numpy as np


#'sedentary': 1.2,
#'lightly_active': 1.375,
#'moderately_active': 1.55,
#'very_active': 1.725,
#'extra_active': 1.9
def calculate_calories(
    gender,
    current_weight,
    goal_weight,
    height,
    age,
    activity_multiplier,
    breastfeeding=False,
    formula="mifflin_st_jeor",
):
    def mifflin_st_jeor(gender, weight, height, age):
        if gender == "male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        elif gender == "female":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            raise ValueError("Invalid gender specified. Use 'male' or 'female'.")
        return bmr

    def harris_benedict_formula(gender, weight, height, age):
        if gender == "male":
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        elif gender == "female":
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
        else:
            raise ValueError("Invalid gender specified. Use 'male' or 'female'.")
        return bmr

    if formula == "mifflin_st_jeor":
        bmr_current = mifflin_st_jeor(gender, current_weight, height, age)
        bmr_goal = mifflin_st_jeor(gender, goal_weight, height, age)
    elif formula == "harris_benedict":
        bmr_current = harris_benedict_formula(gender, current_weight, height, age)
        bmr_goal = harris_benedict_formula(gender, goal_weight, height, age)
    else:
        raise ValueError(
            "Invalid formula specified. Use 'mifflin_st_jeor' or 'harris_benedict'."
        )

    calories_current_maintenance = (
        bmr_current * activity_multiplier + breastfeeding * 500
    )
    calories_goal_maintenance = bmr_goal * activity_multiplier + breastfeeding * 500
    if breastfeeding:
        calories_weight_loss = calories_current_maintenance - 400
    else:
        calories_weight_loss = calories_current_maintenance - 500

    weight_difference = goal_weight - current_weight
    excess_weight = current_weight - goal_weight

    max_excess_weight = 2
    if excess_weight >= max_excess_weight:
        calories_recomendations = calories_weight_loss
    elif excess_weight <= 0:
        calories_recomendations = calories_goal_maintenance
    else:
        interpolation_coefficient = excess_weight / max_excess_weight
        calories_recomendations = (
            calories_goal_maintenance
            + interpolation_coefficient
            * (calories_weight_loss - calories_goal_maintenance)
        )

    return {
        "kcal_current_maintenance": calories_current_maintenance,
        "kcal_goal_maintenance": calories_goal_maintenance,
        "kcal_weight_loss": calories_weight_loss,
        "kcal_recomendations": calories_recomendations,
    }


def calculate_nutrient_ranges(
    gender, height, weight_cur, age, activity_multiplier, breastfeeding=False
):
    params = {}
    optimal_bmi = get_optimal_bmi(gender)
    bmi_ranges = get_bmi_range(height, optimal_bmi)
    weight_ranges = bmi_ranges * height**2
    optimal_weight = weight_ranges[2]

    calories = calculate_calories(
        gender,
        weight_cur,
        optimal_weight,
        height * 100,
        age,
        activity_multiplier,
        breastfeeding=breastfeeding,
    )
    kcal_current_maintenance = calories["kcal_current_maintenance"]
    kcal_recomendations = calories["kcal_recomendations"]
    params["Energ_Kcal"] = get_energy_range(kcal_recomendations)
    params["Protein_(g)"] = get_protein_range(weight_cur)
    params["Lipid_Tot_(g)"] = get_lipid_range(
        kcal_current_maintenance, kcal_recomendations
    )
    params["Carbohydrt_(g)"] = get_carbohydrate_range(
        kcal_recomendations, params["Protein_(g)"][2], params["Lipid_Tot_(g)"][2]
    )
    # params['Sugar_Tot_(g)'] = get_sugar_range(kcal_recomendations)
    params["vegetables_fruits"] = get_vegetable_fruits_range()
    params["FA_Sat_(g)"] = get_saturated_fat_range(kcal_recomendations)
    params["Fiber_TD_(g)"] = get_fiber_range(gender)

    update_vitamins_and_minerals(params, gender, breastfeeding)

    return params


def get_optimal_bmi(gender):
    if gender.lower() == "male":
        return 22.5
    elif gender.lower() == "female":
        return 21.5
    else:
        return 22


def get_bmi_range(height, optimal_bmi):
    return np.array([18.5, optimal_bmi - 1, optimal_bmi, optimal_bmi + 1, 25])


def get_fiber_range(gender):
    if gender.lower() == "male":
        return np.array([25, 30, 38, 45, 70])
    elif gender.lower() == "female":
        return np.array([20, 21, 25, 35, 65])


def get_protein_range(weight_cur):
    return np.array([0.83, 1.2, 1.4, 1.6, 2]) * weight_cur


def get_lipid_range(kcal_current_maintenance, kcal_recomendations):
    return (
        np.array(
            [
                0.2 * kcal_recomendations,
                0.25 * kcal_recomendations,
                0.275 * kcal_recomendations,
                0.275 * kcal_recomendations,
                0.3 * kcal_recomendations,
            ]
        )
        / 9
    )


def get_carbohydrate_range(kcal_recomendations, protein, lipid):
    return np.array(
        [
            130,
            0.45 * kcal_recomendations / 4,
            (kcal_recomendations - protein * 4 - lipid * 9) / 4,
            0.6 * kcal_recomendations / 4,
            0.65 * kcal_recomendations / 4,
        ]
    )


def get_energy_range(kcal_recomendations):
    return np.array(
        [
            kcal_recomendations - 200,
            kcal_recomendations - 100,
            kcal_recomendations,
            kcal_recomendations + 100,
            kcal_recomendations + 200,
        ]
    )


def get_saturated_fat_range(kcal_recomendations):
    return np.array(
        [0, 0, 0, 0.05 * kcal_recomendations / 9, 0.1 * kcal_recomendations / 9]
    )


def get_sugar_range(kcal_recomendations):
    return np.array(
        [0, 0, 0, 0.05 * kcal_recomendations / 4, 0.1 * kcal_recomendations / 4]
    )


def get_vegetable_fruits_range():
    return np.array([400, 400, 800, 1000, 1200])


def get_saturated_fat_range(kcal_recomendations):
    return np.array(
        [0, 0, 0, 0.05 * kcal_recomendations / 9, 0.1 * kcal_recomendations / 9]
    )


def update_vitamins_and_minerals(params, gender, breastfeeding):
    if gender.lower() == "male":
        male_vitamins_and_minerals = {
            "Calcium_(mg)": np.array([800, 1000, 1200, 2000, 2500]),
            "Iron_(mg)": np.array([8, 10, 11, 18, 45]),
            "Magnesium_(mg)": np.array([400, 420, 500, 600, 700]),
            "Phosphorus_(mg)": np.array([800, 1000, 1200, 2500, 4000]),
            "Potassium_(mg)": np.array([2500, 3000, 3400, 5000, 10000]),
            "Sodium_(mg)": np.array([1300, 1500, 1750, 2000, 2300]),
            "Zinc_(mg)": np.array([11, 12, 15, 25, 40]),
            "Copper_mg)": np.array([0.9, 1, 1.5, 3, 10]),
            "Manganese_(mg)": np.array([2.3, 2.3, 2.3, 5, 11]),
            "Selenium_(µg)": np.array([70, 70, 70, 300, 400]),
            "Vit_C_(mg)": np.array([90, 120, 150, 500, 2000]),
            "Thiamin_(mg)": np.array([1.2, 1.6, 2, 5, 10]),
            "Riboflavin_(mg)": np.array([1.3, 1.8, 2, 5, 10]),
            "Niacin_(mg)": np.array([16, 20, 28, 35, 60]),
            "Panto_Acid_mg)": np.array([5, 5, 5, 10, 20]),
            "Vit_B6_(mg)": np.array([1.3, 2, 2, 25, 100]),
            "Folate_Tot_(µg)": np.array([400, 400, 400, 800, 1000]),
            "Choline_Tot_ (mg)": np.array([550, 550, 750, 1000, 3500]),
            "Vit_B12_(µg)": np.array([2.4, 3, 3, 10, 20]),
            "Vit_A_RAE": np.array([900, 1300, 1500, 2000, 3000]),
            "Vit_E_(mg)": np.array([15, 15, 15, 300, 1000]),
            "Vit_D_µg": np.array([10, 15, 40, 50, 100]),
            "Vit_K_(µg)": np.array([120, 200, 250, 300, 500]),
        }
        params.update(male_vitamins_and_minerals)
    elif gender.lower() == "female":
        female_vitamins_and_minerals = get_female_vitamins_and_minerals(breastfeeding)
        params.update(female_vitamins_and_minerals)


def get_female_vitamins_and_minerals(breastfeeding):
    return {
        "Calcium_(mg)": np.array(
            [
                800 + 400 * breastfeeding,
                1000 + 400 * breastfeeding,
                1200 + 400 * breastfeeding,
                2000,
                2500,
            ]
        ),
        "Iron_(mg)": np.array(
            [18, 18 + 9 * breastfeeding, 18 + 9 * breastfeeding, 36, 45]
        ),
        "Magnesium_(mg)": np.array([310, 320, 400, 500, 600]) + 50 * breastfeeding,
        "Phosphorus_(mg)": np.array(
            [
                800 + 200 * breastfeeding,
                1000 + 200 * breastfeeding,
                1200 + 200 * breastfeeding,
                2500,
                4000,
            ]
        ),
        "Potassium_(mg)": np.array([2500, 2600, 3000, 5000, 10000]),
        "Sodium_(mg)": np.array([1300, 1500, 1750, 2000, 2300]),
        "Zinc_(mg)": np.array(
            [10 + 3 * breastfeeding, 12 + 3 * breastfeeding, 15, 25, 40]
        ),
        "Copper_mg)": np.array(
            [
                0.9 + 0.4 * breastfeeding,
                1 + 0.4 * breastfeeding,
                1.5 + 0.4 * breastfeeding,
                3,
                10,
            ]
        ),
        "Manganese_(mg)": np.array(
            [
                1.8 + 0.8 * breastfeeding,
                2 + 0.8 * breastfeeding,
                2 + 0.8 * breastfeeding,
                5,
                11,
            ]
        ),
        "Selenium_(µg)": np.array(
            [
                55 + 15 * breastfeeding,
                55 + 15 * breastfeeding,
                55 + 15 * breastfeeding,
                300,
                400,
            ]
        ),
        "Vit_C_(mg)": np.array(
            [
                90 + 30 * breastfeeding,
                120 + 30 * breastfeeding,
                150 + 30 * breastfeeding,
                500,
                2000,
            ]
        ),
        "Thiamin_(mg)": np.array(
            [
                1.1 + 0.3 * breastfeeding,
                1.5 + 0.3 * breastfeeding,
                1.8 + 0.3 * breastfeeding,
                5 * breastfeeding,
                10,
            ]
        ),
        "Riboflavin_(mg)": np.array(
            [
                1.1 + 0.5 * breastfeeding,
                1.8 + 0.3 * breastfeeding,
                2 + 0.3 * breastfeeding,
                5,
                10,
            ]
        ),
        "Niacin_(mg)": np.array(
            [
                14 + 3 * breastfeeding,
                20 + 3 * breastfeeding,
                20 + 3 * breastfeeding,
                35,
                60,
            ]
        ),
        "Panto_Acid_mg)": np.array(
            [
                5 + 2 * breastfeeding,
                5 + 2 * breastfeeding,
                5 + 2 * breastfeeding,
                10,
                20,
            ]
        ),
        "Vit_B6_(mg)": np.array(
            [
                1.3 + 0.6 * breastfeeding,
                2 + 0.5 * breastfeeding,
                2 + 0.5 * breastfeeding,
                25,
                100,
            ]
        ),
        "Folate_Tot_(µg)": np.array(
            [
                400 + 100 * breastfeeding,
                400 + 100 * breastfeeding,
                400 + 100 * breastfeeding,
                800,
                1000,
            ]
        ),
        "Choline_Tot_ (mg)": np.array(
            [425 + 125 * breastfeeding, 425 + 125 * breastfeeding, 750, 1000, 3500]
        ),
        "Vit_B12_(µg)": np.array(
            [
                2.4 + 0.4 * breastfeeding,
                3 + 0.5 * breastfeeding,
                3 + 0.5 * breastfeeding,
                10,
                20,
            ]
        ),
        "Vit_A_RAE": np.array(
            [
                900 + 400 * breastfeeding,
                1300 + 200 * breastfeeding,
                1500 + 200 * breastfeeding,
                2000,
                3000,
            ]
        ),
        "Vit_E_(mg)": np.array(
            [
                15 + 4 * breastfeeding,
                15 + 4 * breastfeeding,
                15 + 4 * breastfeeding,
                300,
                1000,
            ]
        ),
        "Vit_D_µg": np.array([10, 15, 40, 50, 100]),
        "Vit_D_IU": np.array([10, 15, 40, 50, 100]) * 40,
        "Vit_K_(µg)": np.array([120, 200, 250, 500, 1000]),
    }
