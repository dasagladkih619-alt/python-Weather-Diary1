import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# File for storing weather records
DATA_FILE = "weather_data.json"

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("800x500")

        self.records = []  # list of dicts
        self.load_from_file()

        # --- Input Frame ---
        input_frame = tk.LabelFrame(root, text="Add New Record", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Date
        tk.Label(input_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.date_entry = tk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Temperature
        tk.Label(input_frame, text="Temperature (°C):").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.temp_entry = tk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)

        # Description
        tk.Label(input_frame, text="Description:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.desc_entry = tk.Entry(input_frame, width=50)
        self.desc_entry.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5)

        # Precipitation (Yes/No)
        self.precip_var = tk.BooleanVar()
        tk.Checkbutton(input_frame, text="Precipitation", variable=self.precip_var).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Add button
        tk.Button(input_frame, text="➕ Add Record", command=self.add_record, bg="lightgreen").grid(row=2, column=3, padx=5, pady=5)

        # --- Filter Frame ---
        filter_frame = tk.LabelFrame(root, text="Filter Records", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(filter_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.filter_date_entry = tk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Temp > (°C):").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.filter_temp_entry = tk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(filter_frame, text="Apply Filters", command=self.apply_filters, bg="lightblue").grid(row=0, column=4, padx=10, pady=5)
        tk.Button(filter_frame, text="Show All", command=self.show_all_records, bg="lightgray").grid(row=0, column=5, padx=5, pady=5)

        # --- Treeview (Table) ---
        self.tree = ttk.Treeview(root, columns=("Date", "Temperature", "Description", "Precipitation"), show="headings")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Temperature", text="Temperature (°C)")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Precipitation", text="Precipitation")
        self.tree.column("Date", width=100)
        self.tree.column("Temperature", width=100)
        self.tree.column("Description", width=300)
        self.tree.column("Precipitation", width=100)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Buttons for Save/Load (Manual) ---
        button_frame = tk.Frame(root)
        button_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(button_frame, text="💾 Save to JSON", command=self.save_to_file, bg="lightyellow").pack(side="left", padx=5)
        tk.Button(button_frame, text="📂 Load from JSON", command=self.load_from_file, bg="lightyellow").pack(side="left", padx=5)

        self.show_all_records()

    # ----- Validation -----
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    # ----- Add Record -----
    def add_record(self):
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        # Validation
        if not date or not temp_str or not desc:
            messagebox.showerror("Input Error", "All fields (Date, Temperature, Description) are required.")
            return
        if not self.validate_date(date):
            messagebox.showerror("Input Error", "Invalid date format. Use YYYY-MM-DD.")
            return
        try:
            temp = float(temp_str)
        except ValueError:
            messagebox.showerror("Input Error", "Temperature must be a number.")
            return

        record = {
            "date": date,
            "temperature": temp,
            "description": desc,
            "precipitation": "Yes" if precip else "No"
        }
        self.records.append(record)
        self.show_all_records()

        # Clear inputs
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

        messagebox.showinfo("Success", "Record added!")

    # ----- Filter Logic -----
    def apply_filters(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()

        filtered = self.records[:]

        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Filter Error", "Invalid date format in filter.")
                return
            filtered = [r for r in filtered if r["date"] == filter_date]

        if filter_temp_str:
            try:
                min_temp = float(filter_temp_str)
                filtered = [r for r in filtered if r["temperature"] > min_temp]
            except ValueError:
                messagebox.showerror("Filter Error", "Temperature filter must be a number.")
                return

        self.update_table(filtered)

    def show_all_records(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table(self.records)

    def update_table(self, records_list):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for rec in records_list:
            self.tree.insert("", tk.END, values=(rec["date"], rec["temperature"], rec["description"], rec["precipitation"]))

    # ----- JSON Save/Load -----
    def save_to_file(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Save", f"Data saved to {DATA_FILE}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def load_from_file(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.records = json.load(f)
            self.show_all_records()
            messagebox.showinfo("Load", f"Data loaded from {DATA_FILE}")
        except FileNotFoundError:
            self.records = []
            self.show_all_records()
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
