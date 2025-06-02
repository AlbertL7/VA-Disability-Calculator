'''
References for Creation of Application
    https://www.va.gov/disability/about-disability-ratings/
    https://www.va.gov/vetapp20/Files3/20021766.txt
    http://va.gov/vetapp20/Files1/20002468.txt
    https://www.ecfr.gov/current/title-38/chapter-I/part-4/subpart-A/section-4.25
    https://www.knowva.ebenefits.va.gov/system/templates/selfservice/va_ssnew/help/customer/locale/en-US/portal/554400000001018/content/554400000180525/M21-1-Part-V-Subpart-iv-Chapter-1-Section-C-Coded-Conclusion#4b
'''
import tkinter as tk
from tkinter import messagebox
from typing import List, Dict, Optional, Any

# --- Calculation functions ---
def corrected_va_disability_precise(ratings: List[float]) -> float: 
    """Calculates VA combined rating carrying decimal precision."""
    if not ratings:
        return 0.0
    valid_ratings = sorted([float(r) for r in ratings if float(r) > 0], reverse=True)
    if not valid_ratings:
        return 0.0
    
    combined = float(valid_ratings[0])
    for r_val in valid_ratings[1:]:
        if combined >= 100: 
            combined = 100 
            break
        remaining = 100.0 - combined
        combined += remaining * (float(r_val) / 100.0)
    return round(combined, 4)

def corrected_va_disability_table_method(ratings: List[float]) -> int:
    """
    Calculates VA combined rating by rounding to nearest integer at EACH step,
    mimicking VA tables. Inputs are also treated as integers (rounded if float).
    """
    if not ratings:
        return 0
    
    valid_ratings_int = sorted([int(float(r) + 0.5) for r in ratings if float(r) > 0], reverse=True)
    if not valid_ratings_int:
        return 0
    
    combined_val = float(valid_ratings_int[0]) 

    for r_int in valid_ratings_int[1:]:
        if combined_val >= 100: 
            combined_val = 100 
            break 
        precise_addition = (100.0 - combined_val) * (float(r_int) / 100.0)
        combined_val = int(combined_val + precise_addition + 0.5) 
            
    return int(combined_val + 0.5)

def round_to_va_award(n: float) -> int:
    """Rounds the combined rating to the nearest 10% for the final award."""
    n_rounded_to_integer = int(n + 0.5) 
    last_digit = n_rounded_to_integer % 10
    if last_digit >= 5:
        return ((n_rounded_to_integer // 10) + 1) * 10
    else:
        return (n_rounded_to_integer // 10) * 10

class VADisabilityCalculatorApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("VA Disability Calculator (Corrected Bilateral Logic)")
        master.minsize(550, 700) 

        self.disabilities: List[Dict[str, Any]] = []
        self.selected_display_index: int = -1
        self.last_result_text: str = ""

        self._setup_widgets()
        self._bind_events()
        self.update_display()

    def _setup_widgets(self):
        self.master.grid_rowconfigure(0, weight=1) 
        self.master.grid_columnconfigure(0, weight=1)

        main_frame = tk.Frame(self.master)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        main_frame.grid_rowconfigure(0, weight=0) 
        main_frame.grid_rowconfigure(1, weight=0) 
        main_frame.grid_rowconfigure(2, weight=1) 
        main_frame.grid_rowconfigure(3, weight=0) 
        main_frame.grid_columnconfigure(0, weight=1)

        input_frame = tk.Frame(main_frame, padx=10, pady=5)
        input_frame.grid(row=0, column=0, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        tk.Label(input_frame, text="Enter General Ratings Separated by a Space for Multiple").pack(fill=tk.X)
        general_sub_frame = tk.Frame(input_frame)
        general_sub_frame.pack(fill=tk.X, pady=(0, 5))
        self.entry_general = tk.Entry(general_sub_frame)
        self.entry_general.pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(general_sub_frame, text="Add", command=self.add_general_ratings).pack(side=tk.LEFT, padx=(5,0))

        extremity_frame = tk.Frame(main_frame, padx=10, pady=5)
        extremity_frame.grid(row=1, column=0, sticky="ew")
        extremity_frame.grid_columnconfigure(0, weight=1)

        tk.Label(extremity_frame, text="Enter Extremity Ratings (space-separated for multiple):\n**Right/Left Arm/Leg Refer to all Upper and Lower Service Connected Extremities.**").pack(fill=tk.X)
        
        upper_frame = tk.Frame(extremity_frame)
        upper_frame.pack(fill=tk.X)
        lower_frame = tk.Frame(extremity_frame)
        lower_frame.pack(fill=tk.X, pady=5)
        
        self.extremity_entries: Dict[str, tk.Entry] = {}
        extremity_layout = [
            ("Left Arm", "L", "Upper", upper_frame), 
            ("Right Arm", "R", "Upper", upper_frame),
            ("Left Leg", "L", "Lower", lower_frame),
            ("Right Leg", "R", "Lower", lower_frame)
        ]
        
        for part, side, ext_type, parent_frame in extremity_layout:
            if parent_frame == upper_frame or parent_frame == lower_frame:
                parent_frame.grid_columnconfigure(0, weight=1)
                parent_frame.grid_columnconfigure(1, weight=1)

            sub_frame = tk.Frame(parent_frame)
            sub_frame.pack(side=tk.LEFT, padx=5, pady=2, expand=True, fill=tk.X)
            
            tk.Label(sub_frame, text=f"{part}:").pack(side=tk.LEFT, padx=2)
            entry = tk.Entry(sub_frame)
            entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
            self.extremity_entries[part] = entry
            tk.Button(sub_frame, text="Add", command=lambda p=part, s=side, e=ext_type: self.add_extremity_rating(p, s, e)).pack(side=tk.LEFT, padx=(5,0))

        list_frame = tk.Frame(main_frame, padx=10, pady=5)
        list_frame.grid(row=2, column=0, sticky="nsew") 
        list_frame.grid_rowconfigure(1, weight=1) 
        list_frame.grid_columnconfigure(0, weight=1)

        tk.Label(list_frame, text="Current Disabilities (Select to edit or delete)").grid(row=0, column=0, sticky="w")
        self.ratings_listbox = tk.Listbox(list_frame, height=10) 
        self.ratings_listbox.grid(row=1, column=0, sticky="nsew", pady=5)
        
        edit_frame = tk.Frame(list_frame)
        edit_frame.grid(row=2, column=0, sticky="ew", pady=5)
        edit_frame.grid_columnconfigure(0, weight=1) 
        edit_frame.grid_columnconfigure(4, weight=1) 

        tk.Label(edit_frame, text="Edit Rating:").grid(row=0, column=1, padx=5)
        self.edit_entry = tk.Entry(edit_frame, width=10)
        self.edit_entry.grid(row=0, column=2, padx=5)
        self.update_rating_button = tk.Button(edit_frame, text="Update", command=self.update_selected_rating)
        self.update_rating_button.grid(row=0, column=3)
        self.delete_button = tk.Button(edit_frame, text="Delete Selected", command=self._handle_delete_action)
        self.delete_button.grid(row=0, column=4, padx=5)

        results_frame = tk.Frame(main_frame, padx=10, pady=10)
        results_frame.grid(row=3, column=0, sticky="ew")
        results_frame.grid_columnconfigure(0, weight=1) 

        action_button_frame = tk.Frame(results_frame)
        action_button_frame.pack(fill=tk.X) 
        tk.Button(action_button_frame, text="Calculate", command=self.calculate_total_disability, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.copy_button = tk.Button(action_button_frame, text="Copy Results", command=self.copy_results_to_clipboard, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT, padx=10)
        tk.Button(action_button_frame, text="Clear All", command=self.clear_all).pack(side=tk.RIGHT)
        
        text_area_frame = tk.Frame(results_frame)
        text_area_frame.pack(pady=10, fill=tk.BOTH, expand=True) 
        
        self.result_scrollbar = tk.Scrollbar(text_area_frame, orient=tk.VERTICAL)
        self.result_text_area = tk.Text(text_area_frame, 
                                        wrap=tk.WORD, 
                                        font=("Arial", 10), 
                                        yscrollcommand=self.result_scrollbar.set,
                                        height=10) 
        
        self.result_scrollbar.config(command=self.result_text_area.yview)
        self.result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.result_text_area.config(state=tk.DISABLED) 
        
        tk.Label(self.master, text="Note: Calculations based on 38 CFR § 4.25 & § 4.26, BVA reviewed precedent, and the VA Combined Ratings Table.", fg='gray').grid(row=1, column=0, sticky="ew", pady=(0,5))

    def _bind_events(self):
        self.entry_general.bind('<Return>', self.add_general_ratings)
        for part, entry in self.extremity_entries.items():
            _, side, ext_type = next(p for p in [("Left Arm", "L", "Upper"), ("Right Arm", "R", "Upper"),
                                                 ("Left Leg", "L", "Lower"), ("Right Leg", "R", "Lower")] if p[0] == part)
            entry.bind('<Return>', lambda event, p=part, s=side, e=ext_type: self.add_extremity_rating(p, s, e))
        self.ratings_listbox.bind('<<ListboxSelect>>', self.on_listbox_select)
        self.ratings_listbox.bind('<Double-Button-1>', self._handle_delete_action)
        self.ratings_listbox.bind('<Delete>', self._handle_delete_action)

    def copy_results_to_clipboard(self):
        if not self.last_result_text:
            messagebox.showwarning("No Results", "There are no results to copy. Please calculate first.")
            return
        self.master.clipboard_clear()
        self.master.clipboard_append(self.last_result_text)
        messagebox.showinfo("Copied", "The results have been copied to your clipboard.")

    def add_general_ratings(self, event: Optional[tk.Event] = None):
        ratings_str = self.entry_general.get()
        if not ratings_str.strip(): return
        try:
            ratings = [float(r) for r in ratings_str.split()]
            for rating in ratings:
                if 0 <= rating <= 100: self.disabilities.append({'body_part': 'General', 'rating': rating, 'side': None, 'extremity_type': None})
                else: messagebox.showwarning("Invalid Rating", f"Rating '{rating}' is out of range (0-100) and was skipped.")
            self.entry_general.delete(0, tk.END)
            self.update_display()
        except ValueError: messagebox.showerror("Invalid Input", "Please enter valid numbers separated by spaces.")

    def add_extremity_rating(self, body_part: str, side: str, extremity_type: str, event: Optional[tk.Event] = None):
        entry_widget = self.extremity_entries[body_part]
        ratings_str = entry_widget.get()
        if not ratings_str.strip(): return
        try:
            ratings = [float(r) for r in ratings_str.split()]
            for rating in ratings:
                if 0 <= rating <= 100: self.disabilities.append({'body_part': body_part, 'rating': rating, 'side': side, 'extremity_type': extremity_type})
                else: messagebox.showwarning("Invalid Rating", f"Rating '{rating}' is out of range (0-100) and was skipped.")
            entry_widget.delete(0, tk.END)
            self.update_display()
        except ValueError: messagebox.showerror("Invalid Input", f"Please enter valid numbers for {body_part}.")

    def update_display(self):
        self.ratings_listbox.delete(0, tk.END)
        if not self.disabilities:
            self.ratings_listbox.insert(tk.END, "No disabilities entered yet.")
            self.ratings_listbox.config(fg='grey')
            self._set_edit_controls_state(tk.DISABLED)
        else:
            self.ratings_listbox.config(fg='black')
            for i, disc in enumerate(self.disabilities):
                display_rating = f"{disc['rating']:.2f}".rstrip('0').rstrip('.') if isinstance(disc['rating'], float) else f"{int(disc['rating'])}"
                display_text = f"{i+1}. {disc['body_part']}: {display_rating}%"
                self.ratings_listbox.insert(tk.END, display_text)
            self.on_listbox_select()
        
        if hasattr(self, 'result_text_area'):
            self.result_text_area.config(state=tk.NORMAL)
            self.result_text_area.delete('1.0', tk.END)
            self.result_text_area.config(state=tk.DISABLED)
        self.last_result_text = ""
        if hasattr(self, 'copy_button'): 
            self.copy_button.config(state=tk.DISABLED)

    def on_listbox_select(self, event: Optional[tk.Event] = None):
        selected_indices = self.ratings_listbox.curselection()
        if selected_indices and self.disabilities:
            self.selected_display_index = selected_indices[0]
            selected_disability = self.disabilities[self.selected_display_index]
            self.edit_entry.delete(0, tk.END)
            self.edit_entry.insert(0, str(selected_disability['rating']))
            self._set_edit_controls_state(tk.NORMAL)
        else:
            self.selected_display_index = -1
            self.edit_entry.delete(0, tk.END)
            self._set_edit_controls_state(tk.DISABLED)

    def update_selected_rating(self):
        if self.selected_display_index == -1: return
        try:
            new_rating = float(self.edit_entry.get())
            if 0 <= new_rating <= 100:
                self.disabilities[self.selected_display_index]['rating'] = new_rating
                self.update_display()
            else: messagebox.showerror("Invalid Input", "Rating must be between 0 and 100.")
        except ValueError: messagebox.showerror("Invalid Input", "Please enter a valid number.")

    def _handle_delete_action(self, event: Optional[tk.Event] = None):
        selected_indices = self.ratings_listbox.curselection()
        if not selected_indices or not self.disabilities: return
        index_to_delete = selected_indices[0] 
        disability_to_delete = self.disabilities[index_to_delete] 
        prompt = f"Are you sure you want to delete this disability?\n\n- {disability_to_delete['body_part']}: {disability_to_delete['rating']}%"
        if messagebox.askyesno("Confirm Delete", prompt):
            del self.disabilities[index_to_delete]
            self.update_display()

    def clear_all(self):
        if self.disabilities and messagebox.askyesno("Confirm Clear", "Are you sure you want to clear ALL ratings?"):
            self.disabilities = []
            self.update_display()
            for entry_widget in self.extremity_entries.values(): entry_widget.delete(0, tk.END)
            self.entry_general.delete(0, tk.END)

    def _set_edit_controls_state(self, state: str):
        self.edit_entry.config(state=state)
        self.update_rating_button.config(state=state)
        delete_state = state if self.selected_display_index != -1 and self.ratings_listbox.curselection() else tk.DISABLED
        self.delete_button.config(state=delete_state)

    def calculate_total_disability(self):
        if not self.disabilities:
            messagebox.showwarning("No Ratings", "Please enter at least one disability rating.")
            return

        general_ratings_orig, upper_l_orig, upper_r_orig, lower_l_orig, lower_r_orig = [], [], [], [], []
        for disc in self.disabilities:
            rating = float(disc['rating'])
            if rating > 0:
                if disc['extremity_type'] == 'Upper':
                    if disc['side'] == 'L': upper_l_orig.append(rating)
                    elif disc['side'] == 'R': upper_r_orig.append(rating)
                elif disc['extremity_type'] == 'Lower':
                    if disc['side'] == 'L': lower_l_orig.append(rating)
                    elif disc['side'] == 'R': lower_r_orig.append(rating)
                else:
                    general_ratings_orig.append(rating)
        
        # *** Corrected process_bilateral_... functions to handle the condition properly ***
        def process_bilateral_bva(left_ratings, right_ratings):
            is_truly_bilateral = bool(left_ratings and right_ratings) # Bilateral factor ONLY if ratings on BOTH sides
            
            all_limb_ratings_for_base_calc = left_ratings + right_ratings
            base_combined_precise = corrected_va_disability_precise(all_limb_ratings_for_base_calc)
            
            factor_precise = 0.0
            value_with_factor_unrounded = base_combined_precise # Start with base

            if is_truly_bilateral and base_combined_precise > 0:
                factor_precise = round(base_combined_precise * 0.1, 4)
                value_with_factor_unrounded = base_combined_precise + factor_precise
            
            rounded_value_int = int(value_with_factor_unrounded + 0.5)
            return (rounded_value_int, factor_precise, base_combined_precise, value_with_factor_unrounded, is_truly_bilateral)

        def process_bilateral_table(left_ratings, right_ratings):
            is_truly_bilateral = bool(left_ratings and right_ratings)

            all_limb_ratings_for_base_calc = left_ratings + right_ratings
            base_combined_int = corrected_va_disability_table_method(all_limb_ratings_for_base_calc)
            
            factor_precise = 0.0
            value_with_factor_unrounded = float(base_combined_int)

            if is_truly_bilateral and base_combined_int > 0:
                factor_precise = round(float(base_combined_int) * 0.1, 4)
                value_with_factor_unrounded = float(base_combined_int) + factor_precise
            
            rounded_value_int = int(value_with_factor_unrounded + 0.5)
            return (rounded_value_int, factor_precise, float(base_combined_int), value_with_factor_unrounded, is_truly_bilateral)

        result_text = ""
        
        # --- Method 1: BVA-Accurate Calculation ---
        result_text += "▂ ▃ ▄ ▅ ▆ ▇ █ BVA-Accurate Method (Precise Combinations) █ ▇ ▆ ▅ ▄ ▃ ▂\n\n"
        final_ratings_bva = []
        
        upper_rounded_bva, upper_factor_bva, upper_base_bva, upper_unrounded_bva, upper_is_bilateral = process_bilateral_bva(upper_l_orig, upper_r_orig)
        if upper_is_bilateral and upper_factor_bva > 0: # Bilateral processing occurred
            result_text += "***Upper Extremities (Bilateral):***\n"
            result_text += f"\tCombining Upper Bilateral Factor Disabilities:\n\t\t {sorted([float(r) for r in upper_l_orig + upper_r_orig], reverse=True)}\n"
            result_text += f"\tBase Value Bilateral Factor (Precise):\n\t\t {upper_base_bva:.2f}%\n"
            result_text += f"\t10% Bonus Factor:\n\t +{upper_factor_bva:.2f}%\n"
            result_text += f"\t% Before Bilateral Factor Integer Rounding:\n\t\t {upper_unrounded_bva:.2f}%\n"
            result_text += f"\t% Rounded Bilateral Integer Replacement Value:\n\t\t {upper_rounded_bva}%\n\n"
            if upper_rounded_bva > 0:
                 final_ratings_bva.append({'value': float(upper_rounded_bva), 'source': "Upper Ext. (Bilateral)"})
        elif upper_l_orig or upper_r_orig: # Ratings exist but not bilateral, or bilateral but 0% result
            result_text += "***Upper Arm (Individual Ratings - Bilateral Factor Not Applied):***\n"
            for r in sorted(upper_l_orig, reverse=True):
                result_text += f"\tLeft Arm Disability:\n\t\t {r}%\n\n"
                final_ratings_bva.append({'value': float(r), 'source': 'Upper Arm - Left'})
            for r in sorted(upper_r_orig, reverse=True):
                result_text += f"\tRight Arm Disability:\n\t\t {r}%\n\n"
                final_ratings_bva.append({'value': float(r), 'source': 'Upper Arm - Right'})
            if not (upper_l_orig or upper_r_orig): # If somehow base was 0 from no inputs
                 if upper_rounded_bva > 0 : final_ratings_bva.append({'value': float(upper_rounded_bva), 'source': "Upper Arm"})


        lower_rounded_bva, lower_factor_bva, lower_base_bva, lower_unrounded_bva, lower_is_bilateral = process_bilateral_bva(lower_l_orig, lower_r_orig)
        if lower_is_bilateral and lower_factor_bva > 0:
            result_text += "***Lower Extremities (Bilateral):***\n"
            result_text += f"\tCombining Lower Bilateral Factor Disabilities:\n\t\t {sorted([float(r) for r in lower_l_orig + lower_r_orig], reverse=True)}\n"
            result_text += f"\tBase Value Bilateral Factor (Precise):\n\t\t {lower_base_bva:.2f}%\n"
            result_text += f"\t10% Bonus Factor:\n\t\t +{lower_factor_bva:.2f}%\n"
            result_text += f"\t% Before Bilateral Factor Integer Rounding:\n\t\t {lower_unrounded_bva:.2f}%\n"
            result_text += f"\t% After Bilateral Factor Integer Rounding:\n\t\t {lower_rounded_bva}%\n\n"
            if lower_rounded_bva > 0:
                final_ratings_bva.append({'value': float(lower_rounded_bva), 'source': "Lower Ext. (Bilateral)"})
        elif lower_l_orig or lower_r_orig:
            result_text += "***Lower Leg (Individual Ratings - Bilateral Factor Not Applied):***\n"
            for r in sorted(lower_l_orig, reverse=True):
                result_text += f"\tLeft Leg Disability:\n\t\t {r}%\n\n"
                final_ratings_bva.append({'value': float(r), 'source': 'Lower Leg - Left'})
            for r in sorted(lower_r_orig, reverse=True):
                result_text += f"\tRight Leg Disability:\n\t\t {r}%\n\n"
                final_ratings_bva.append({'value': float(r), 'source': 'Lower Leg - Right'})
            if not (lower_l_orig or lower_r_orig):
                if lower_rounded_bva > 0 : final_ratings_bva.append({'value': float(lower_rounded_bva), 'source': "Lower Leg"})


        for r_gen_val in general_ratings_orig: final_ratings_bva.append({'value': float(r_gen_val), 'source': 'General'})
        final_ratings_bva.sort(key=lambda x: x['value'], reverse=True)
        
        # Filter out 0% values before final combination for BVA method, unless it's the only rating.
        bva_math_ratings = [item['value'] for item in final_ratings_bva if item['value'] > 0]
        if not bva_math_ratings and final_ratings_bva: # Handle case where all ratings are 0
            bva_math_ratings = [0.0] if final_ratings_bva else []

        combined_bva = corrected_va_disability_precise(bva_math_ratings)
        award_bva = round_to_va_award(combined_bva) 

        bva_breakdown_list = []
        for item in final_ratings_bva:
            display_val = f"{int(item['value'])}" if item['value'] == int(item['value']) else f"{item['value']:.2f}".rstrip('0').rstrip('.')
            source_text = f" ({item['source']})" if item['source'] != 'General' else ""
            bold_char = " " if "Ext. (Bilateral)" in item['source'] else ""
            bva_breakdown_list.append(f"{bold_char}{display_val}%{source_text}{bold_char}")
        
        if final_ratings_bva: result_text += f"***Final Combination List:***\n\t [{', '.join(bva_breakdown_list)}]\n"
        result_text += f"Final Unrounded (Precise):\n\t {combined_bva:.2f}%\n"
        result_text += f"Final Award:\n\t {award_bva}%\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        # --- Method 2: Online Calculator (Table Method) Simulation ---
        result_text += "\n▂ ▃ ▄ ▅ ▆ ▇ █ Combined Ratings Table Method (Step-Wise Rounding) █ ▇ ▆ ▅ ▄ ▃ ▂\n\n"
        final_ratings_table = []

        upper_rounded_tbl, upper_factor_tbl, upper_base_tbl, upper_unrounded_tbl, upper_is_bilateral_tbl = process_bilateral_table(upper_l_orig, upper_r_orig)
        if upper_is_bilateral_tbl and upper_factor_tbl > 0:
            result_text += "***Upper Extremities (Bilateral):***\n"
            result_text += f"\tCombining Bilateral Factor Disabilities (Inputs Rounded):\n\t\t {sorted([int(float(r)+0.5) for r in upper_l_orig + upper_r_orig], reverse=True)}\n"
            result_text += f"\tBase Value (Step-Rounded):\n\t\t {upper_base_tbl:.0f}%\n"
            result_text += f"\t10% Bonus Factor:\n\t\t +{upper_factor_tbl:.2f}%\n"
            result_text += f"\t% Before Bilateral Factor Rounding:\n\t\t {upper_unrounded_tbl:.2f}%\n"
            result_text += f"\t% After Bilateral Factor Rounding:\n\t\t {upper_rounded_tbl}%\n\n"
            if upper_rounded_tbl > 0:
                final_ratings_table.append({'value': float(upper_rounded_tbl), 'source': "Upper Ext. (Bilateral)"})
        elif upper_l_orig or upper_r_orig:
            result_text += "***Upper Arm (Individual Ratings - Bilateral Factor Not Applied):***\n"
            for r_orig_val in sorted(upper_l_orig, reverse=True):
                r = int(float(r_orig_val) + 0.5)
                result_text += f"\tLeft Arm Disability:\n\t\t {r}%\n"
                final_ratings_table.append({'value': float(r), 'source': 'Upper Arm - Left'})
            for r_orig_val in sorted(upper_r_orig, reverse=True):
                r = int(float(r_orig_val) + 0.5)
                result_text += f"\tRight Arm Disability:\n\t\t {r}%\n"
                final_ratings_table.append({'value': float(r), 'source': 'Upper Arm - Right'})
            if not (upper_l_orig or upper_r_orig):
                 if upper_rounded_tbl > 0 : final_ratings_table.append({'value': float(upper_rounded_tbl), 'source': "Upper Arm"})

        lower_rounded_tbl, lower_factor_tbl, lower_base_tbl, lower_unrounded_tbl, lower_is_bilateral_tbl = process_bilateral_table(lower_l_orig, lower_r_orig)
        if lower_is_bilateral_tbl and lower_factor_tbl > 0:
            result_text += "\n***Lower Extremities (Bilateral):***\n"
            result_text += f"\tCombining Bilateral Factor Disabilities (Inputs Rounded):\n\t\t {sorted([int(float(r)+0.5) for r in lower_l_orig + lower_r_orig], reverse=True)}\n"
            result_text += f"\tBase Value (Step-Rounded):\n\t\t {lower_base_tbl:.0f}%\n"
            result_text += f"\t10% Bonus Factor:\n\t\t +{lower_factor_tbl:.2f}%\n"
            result_text += f"\tBefore Bilateral Factor Rounding:\n\t\t {lower_unrounded_tbl:.2f}%\n"
            result_text += f"\tAfter Bilateral Factor Rounding:\n\t\t {lower_rounded_tbl}%\n\n"
            if lower_rounded_tbl > 0:
                final_ratings_table.append({'value': float(lower_rounded_tbl), 'source': "Lower Ext. (Bilateral)"})
        elif lower_l_orig or lower_r_orig:
            result_text += "***Lower Leg (Individual Ratings - Bilateral Factor Not Applied):***\n"
            for r_orig_val in sorted(lower_l_orig, reverse=True):
                r = int(float(r_orig_val) + 0.5)
                result_text += f"\tLeft Leg Disability:\n\t\t {r}%\n\n"
                final_ratings_table.append({'value': float(r), 'source': 'Lower Leg - Left'})
            for r_orig_val in sorted(lower_r_orig, reverse=True):
                r = int(float(r_orig_val) + 0.5)
                result_text += f"\tRight Leg Disability:\n\t\t {r}%\n\n"
                final_ratings_table.append({'value': float(r), 'source': 'Lower Leg - Right'})
            if not (lower_l_orig or lower_r_orig):
                if lower_rounded_tbl > 0 : final_ratings_table.append({'value': float(lower_rounded_tbl), 'source': "Lower Leg"})

        for r_gen_val in general_ratings_orig: final_ratings_table.append({'value': float(r_gen_val), 'source': 'General'})
        final_ratings_table.sort(key=lambda x: x['value'], reverse=True)

        table_breakdown_list = []
        for item in final_ratings_table:
            display_val = f"{int(item['value']+0.5)}" 
            source_text = f" ({item['source']})" if item['source'] != 'General' else ""
            bold_char = " " if "Ext. (Bilateral)" in item['source'] else ""
            table_breakdown_list.append(f"{bold_char}{display_val}%{source_text}{bold_char}")

        if final_ratings_table: result_text += f"***Final Combination List:***\n\t [{', '.join(table_breakdown_list)}]\n"
        
        ratings_for_table_math = [item['value'] for item in final_ratings_table if item['value'] > 0]
        if not ratings_for_table_math and final_ratings_table:
            ratings_for_table_math = [0.0] if final_ratings_table else []

        combined_table_method = float(corrected_va_disability_table_method(ratings_for_table_math))
        award_table_method = round_to_va_award(combined_table_method) 
        result_text += f"Final Unrounded (Step-Rounded):\n\t {combined_table_method:.0f}%\n" 
        result_text += f"Final Award:\n\t {award_table_method}%\n"

        # --- Method 3: Without Bilateral Factor (for comparison) ---
        ratings_without_any_bilateral_factor = []
        # Use BVA method's base values (precise, then rounded) before any factor
        if upper_l_orig or upper_r_orig: # If there were any upper ratings
            for r in upper_l_orig + upper_r_orig:
                 ratings_without_any_bilateral_factor.append(float(r))
        if lower_l_orig or lower_r_orig: # If there were any lower ratings
            for r in lower_l_orig + lower_r_orig:
                 ratings_without_any_bilateral_factor.append(float(r))
        ratings_without_any_bilateral_factor.extend([float(r) for r in general_ratings_orig])
        
        if ratings_without_any_bilateral_factor:
            combined_no_bilateral = corrected_va_disability_precise(ratings_without_any_bilateral_factor)
            award_no_bilateral = round_to_va_award(combined_no_bilateral)
            if award_bva != award_no_bilateral or award_table_method != award_no_bilateral : 
                result_text += "\n\n--- For Comparison (Original Ratings, No Bilateral Factor Applied) ---\n"
                result_text += f"Final Award Would Be:\n\t {award_no_bilateral}%\n"
        
        self.last_result_text = result_text
        self.result_text_area.config(state=tk.NORMAL)
        self.result_text_area.delete('1.0', tk.END)
        self.result_text_area.insert(tk.END, self.last_result_text)
        self.result_text_area.config(state=tk.DISABLED)
        
        if hasattr(self, 'copy_button'): 
             self.copy_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = VADisabilityCalculatorApp(root)
    root.mainloop()
