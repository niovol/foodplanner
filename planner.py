import os
import re
import tkinter as tk
from tkinter import filedialog, ttk

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from AutocompleteWidget import AutocompleteEntry
from data import compute_data_dict, load_json, save_json
from nutrient_ranges import calculate_nutrient_ranges


def plot_ration_nutrients(nutrient_ranges, ration_nutrients, title=""):
    fig = plt.figure(figsize=(12, 24))
    num_bars = len(nutrient_ranges)
    bar_height = 0.5
    ind = np.arange(num_bars)
    colors = ["red", "orange", "green", "orange", "red"]
    bar_colors = ["red", "orange", "green", "green", "orange", "red"]

    for nutrient_idx, nutrient in enumerate(nutrient_ranges):
        normalized_nutrient_values = [
            value / max(nutrient_ranges[nutrient])
            for value in nutrient_ranges[nutrient]
        ]
        normalized_current_value = min(
            ration_nutrients.get(nutrient, 0) / max(nutrient_ranges[nutrient]), 1
        )
        range_idx = np.searchsorted(
            nutrient_ranges[nutrient], ration_nutrients.get(nutrient, 0)
        )
        bar_color = bar_colors[range_idx]
        plt.barh(
            num_bars - 1 - ind[nutrient_idx],
            normalized_current_value,
            height=bar_height,
            color=bar_color,
            alpha=0.8,
            label=nutrient,
        )

        for i, value in enumerate(normalized_nutrient_values):
            plt.plot(
                [value, value],
                [
                    num_bars - 1 - ind[nutrient_idx] - 0.5 * bar_height,
                    num_bars - 1 - ind[nutrient_idx] + 0.5 * bar_height,
                ],
                color=colors[i],
                linestyle="--",
                linewidth=1.5,
            )
            plt.text(
                value,
                num_bars - 1 - ind[nutrient_idx] + 0.55 * bar_height,
                f"{nutrient_ranges[nutrient][i]:.1f}",
                fontsize=9,
                color=colors[i],
            )

        plt.text(
            0.01,
            -0.1 + num_bars - 1 - ind[nutrient_idx],
            f"{ration_nutrients.get(nutrient, 0):.1f}",
            fontsize=10,
            color="black",
            bbox=dict(facecolor="white", edgecolor="none", pad=1),
        )

    plt.yticks(num_bars - 1 - ind, nutrient_ranges.keys())
    plt.xlabel("Normalized Values")
    plt.ylabel("Nutrients")
    plt.title(title)
    return fig


class DishWeightEntry(tk.Frame):
    def __init__(
        self,
        autocomplete_list,
        remove_callback,
        disable_autocomplete=False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.dish_entry = AutocompleteEntry(
            autocomplete_list, disable_autocomplete=disable_autocomplete, master=self
        )
        self.dish_entry.grid(row=0, column=0)

        self.weight_entry = tk.Entry(self, width=10)
        self.weight_entry.grid(row=0, column=1)

        self.remove_button = tk.Button(self, text="X")
        self.remove_button.grid(row=0, column=2)
        self.remove_button.config(command=lambda: remove_callback(self))


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.data = load_json("food_database.json")

        self.title("Nutrient Ration Planner")
        self.geometry("1600x900")

        self.dish_weight_entries = []

        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.save_physiological_params_button = tk.Button(
            self.left_frame,
            text="Save Physiological Params",
            command=self.save_physiological_params,
        )
        self.save_physiological_params_button.pack()

        self.load_physiological_params_button = tk.Button(
            self.left_frame,
            text="Load Physiological Params",
            command=self.load_physiological_params,
        )
        self.load_physiological_params_button.pack()

        self.gender_var = tk.StringVar(self, value="male")
        tk.Label(self.left_frame, text="Gender:").pack()
        self.gender_dropdown = ttk.Combobox(
            self.left_frame,
            textvariable=self.gender_var,
            values=["male", "female"],
            state="readonly",
        )
        self.gender_dropdown.pack()

        self.height_var = tk.DoubleVar(self, value=1.75)
        tk.Label(self.left_frame, text="Height (m):").pack()
        self.height_entry = ttk.Entry(self.left_frame, textvariable=self.height_var)
        self.height_entry.pack()

        self.weight_var = tk.DoubleVar(self, value=70.0)
        tk.Label(self.left_frame, text="Weight (kg):").pack()
        self.weight_entry = ttk.Entry(self.left_frame, textvariable=self.weight_var)
        self.weight_entry.pack()

        self.age_var = tk.IntVar(self, value=30)
        tk.Label(self.left_frame, text="Age:").pack()
        self.age_entry = ttk.Entry(self.left_frame, textvariable=self.age_var)
        self.age_entry.pack()

        self.activity_multiplier_var = tk.DoubleVar(self, value=1.3)
        tk.Label(self.left_frame, text="Activity Multiplier:").pack()
        self.activity_multiplier_entry = ttk.Entry(
            self.left_frame, textvariable=self.activity_multiplier_var
        )
        self.activity_multiplier_entry.pack()

        self.breastfeeding_var = tk.BooleanVar(self, value=False)
        tk.Label(self.left_frame, text="Breastfeeding:").pack()
        self.breastfeeding_check = ttk.Checkbutton(
            self.left_frame, variable=self.breastfeeding_var
        )
        self.breastfeeding_check.pack()

        self.save_button = tk.Button(
            self.left_frame, text="Save Ration", command=self.save_ration
        )
        self.save_button.pack()

        self.load_button = tk.Button(
            self.left_frame, text="Load Ration", command=self.load_ration
        )
        self.load_button.pack()

        self.export_button = tk.Button(
            self.left_frame, text="Export Plot", command=self.export_plot
        )
        self.export_button.pack()

        self.add_dish_button = tk.Button(
            self.left_frame, text="Add Dish", command=self.add_dish_field
        )
        self.add_dish_button.pack()

        self.plot_button = tk.Button(
            self.left_frame, text="Plot", command=self.plot_ration_nutrients
        )
        self.plot_button.pack()

        self.add_dish_field()

        self.canvas = None

    def save_physiological_params(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not file_path:
            return

        physiological_params = {
            "gender": self.gender_var.get(),
            "height": self.height_var.get(),
            "weight": self.weight_var.get(),
            "age": self.age_var.get(),
            "activity_multiplier": self.activity_multiplier_var.get(),
            "breastfeeding": self.breastfeeding_var.get(),
        }

        save_json(file_path, physiological_params)

    def load_physiological_params(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not file_path:
            return

        physiological_params = load_json(file_path)

        self.gender_var.set(physiological_params["gender"])
        self.height_var.set(physiological_params["height"])
        self.weight_var.set(physiological_params["weight"])
        self.age_var.set(physiological_params["age"])
        self.activity_multiplier_var.set(physiological_params["activity_multiplier"])
        self.breastfeeding_var.set(physiological_params["breastfeeding"])

    def draw_plot(self, fig):
        if self.canvas:
            self.canvas.get_tk_widget().pack_forget()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def add_dish_field(self):
        dish_weight_entry = DishWeightEntry(
            list(self.data.keys()),
            remove_callback=self.remove_dish_field,
            master=self.left_frame,
        )
        dish_weight_entry.pack()
        self.dish_weight_entries.append(dish_weight_entry)

    def remove_dish_field(self, dish_weight_entry):
        dish_weight_entry.destroy()
        self.dish_weight_entries.remove(dish_weight_entry)

    def save_ration(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not file_path:
            return

        ration_dict = self.get_current_ration_dict()
        save_json(file_path, ration_dict)

    def load_ration(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not file_path:
            return

        ration_dict = load_json(file_path)

        self.remove_all_dish_fields()

        for dish, weight in ration_dict["Рацион"].items():
            dish_weight_entry = DishWeightEntry(
                list(self.data.keys()),
                remove_callback=self.remove_dish_field,
                disable_autocomplete=True,
                master=self.left_frame,
            )
            dish_weight_entry.dish_entry.insert(0, dish)
            dish_weight_entry.weight_entry.insert(0, str(weight))
            dish_weight_entry.pack()
            dish_weight_entry.dish_entry.config(state="disabled")
            self.dish_weight_entries.append(dish_weight_entry)

    def export_plot(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        )
        if not file_path:
            return

        if self.canvas:
            fig = self.canvas.figure
            fig.savefig(file_path, dpi=300)

    def get_current_ration_dict(self):
        ration_dict = {"Рацион": {}}
        for dish_weight_entry in self.dish_weight_entries:
            dish = dish_weight_entry.dish_entry.get()
            try:
                weight = float(dish_weight_entry.weight_entry.get())
            except ValueError:
                weight = 0

            if dish and weight:
                ration_dict["Рацион"][dish] = weight
        return ration_dict

    def remove_all_dish_fields(self):
        while self.dish_weight_entries:
            dish_weight_entry = self.dish_weight_entries.pop()
            dish_weight_entry.destroy()

    def plot_ration_nutrients(self):
        gender = self.gender_var.get()
        height = self.height_var.get()
        weight = self.weight_var.get()
        age = self.age_var.get()
        activity_multiplier = self.activity_multiplier_var.get()
        breastfeeding = self.breastfeeding_var.get()

        nutrient_ranges = calculate_nutrient_ranges(
            gender, height, weight, age, activity_multiplier, breastfeeding
        )

        ration_dict = self.get_current_ration_dict()
        nutrients_total = compute_data_dict(ration_dict, self.data)["Рацион"][
            "nutrients_total"
        ]
        fig = plot_ration_nutrients(nutrient_ranges, nutrients_total, title=None)
        self.draw_plot(fig)


app = App()
app.mainloop()
