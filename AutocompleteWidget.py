import tkinter as tk
from tkinter import ttk


class AutocompleteEntry(ttk.Entry):
    def __init__(self, autocomplete_list, disable_autocomplete=False, *args, **kwargs):
        self.var = tk.StringVar()
        kwargs["textvariable"] = self.var
        kwargs["width"] = 50
        super().__init__(*args, **kwargs)
        self.autocomplete_list = autocomplete_list
        self.disable_autocomplete = disable_autocomplete
        self._initialize_autocomplete()

    def _initialize_autocomplete(self):
        if not self.disable_autocomplete:
            self.var.trace("w", self.update_list)
        self.listbox = None
        self.toplevel = None
        self.bind("<Control-a>", self.select_all)

    def update_list(self, *args):
        if not self.toplevel:
            self._create_listbox()
        search_text = self.var.get()
        self._filter_listbox(search_text)

    def _create_listbox(self):
        self.toplevel = tk.Toplevel(self)
        self.toplevel.geometry(
            f"+{self.winfo_rootx()}+{self.winfo_rooty() + self.winfo_height()}"
        )
        self.toplevel.overrideredirect(True)
        self.toplevel.config(bg="white")
        self.listbox = tk.Listbox(self.toplevel, width=self["width"], bd=0)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<Double-1>", self.selection)

    def _filter_listbox(self, search_text):
        self.listbox.delete(0, tk.END)
        filtered_autocomplete_list = [
            item
            for item in self.autocomplete_list
            if search_text.lower() in item.lower()
        ]
        for item in filtered_autocomplete_list:
            self.listbox.insert(tk.END, item)

    def selection(self, event):
        if self.listbox:
            self.var.set(self.listbox.get(tk.ACTIVE))
            self._destroy_listbox()
            self.config(state="disabled")

    def _destroy_listbox(self):
        self.toplevel.destroy()
        self.toplevel = None
        self.listbox = None

    def select_all(self, event):
        self.selection_range(0, tk.END)
        return "break"
