# You need tkinter installed "sudo pip install tk" / "pip install tk"

import tkinter as tk
from tkinter import messagebox

def calculate_va_disability(ratings):
    sorted_ratings = sorted(ratings, reverse=True)
    combined_rating = sorted_ratings[0]
    for rating in sorted_ratings[1:]:
        remaining_ability = 100 - combined_rating
        combined_rating += remaining_ability * (rating / 100)
    return combined_rating

def round_to_nearest_ten(n):
    return round(n / 10) * 10

def calculate():
    try:
        ratings = list(map(int, entry.get().split()))
        if not all(0 <= r <= 100 for r in ratings):
            messagebox.showerror("Error", "Ratings must be between 0 and 100.")
            return
        
        actual_disability_rating = calculate_va_disability(ratings)
        awarded_disability_rating = round_to_nearest_ten(actual_disability_rating)
        # Format output to show only two decimal places
        formatted_actual_rating = f"{actual_disability_rating:.2f}"
        formatted_awarded_rating = f"{awarded_disability_rating:.2f}"
        result.config(text=f"Actual Disability Rating: {formatted_actual_rating}%\nAwarded Disability Rating: {formatted_awarded_rating}%")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid integer ratings separated by spaces.")


root = tk.Tk()
root.title("VA Disability Calculator")

tk.Label(root, text="Enter disability ratings separated by spaces:").pack()
entry = tk.Entry(root, width=50)
entry.pack()

calculate_button = tk.Button(root, text="Calculate", command=calculate)
calculate_button.pack()

note = tk.Label(root, text="Note: Awarded % may be wrong, if 5 or greater round up to the nearest 10th.", fg='gray')
note.pack()

result = tk.Label(root, text="")
result.pack()

root.mainloop()
