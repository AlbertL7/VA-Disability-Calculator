## US VA Disability Calculator

Very simple and easy-to-use VA disability calculator for veterans, VSOs, and anyone wanting accurate combined disability ratings. Built to follow 38 CFR § 4.25 and § 4.26 as precisely as possible.

---

## ✅ Features

- Input multiple disability percentages (e.g., `30 10 20`)
- Automatically detects **bilateral limbs** and applies the **10% bilateral factor** correctly
- Compares:
  - ✅ **BVA-Accurate (Precise Method)**
  - 🔁 **VA Table Method (Rounded Step-Wise)**
  - 🧾 **Unadjusted (No Bilateral Factor)**
- Copy final results to clipboard
- Update or delete individual entries
- Clean, interactive GUI built with Tkinter

---

## 💡 How VA Disability is Calculated

1. **List of Disabilities**: Start with each condition’s percentage rating.
2. **Sort Percentages**: From **highest to lowest**.
3. **Combine Using the "Whole Person" Method**:
   - Begin with the highest rating
   - For each next rating:
     - Multiply it by the **remaining ability** (i.e., `100 - current combined`)
     - Add that result to your running total
4. **Round to Nearest 10**: The VA awards by rounding to the nearest 10. For example:
   - 54% becomes **50%**
   - 55% becomes **60%**

---

## 🤔 What Is the Bilateral Factor?

If you have **disabilities affecting both arms, both legs, or paired extremities** (e.g., left & right knee), the **VA adds a 10% bonus** to the combined value of those paired conditions.

This application:
- Detects eligible **paired limbs** automatically (left/right arms or legs)
- Adds **10% of their combined value**
- Includes this before calculating your final disability rating

**Example**:
- Left Arm: 20%
- Right Arm: 20%

Combined = `36%` → 10% of that is `3.6%` → Final = `39.6%` → Rounded to **40%**

---

## 📸 Screenshot

![2025-06-01 19_16_46-Settings](https://github.com/user-attachments/assets/2d1ede2a-abf1-4bac-85c0-542d4ebc493f)

---

## 🧠 Legal Disclaimer

This tool is **not affiliated with the U.S. Department of Veterans Affairs**. It is based on publicly documented rules and helps provide more transparency and understanding of VA math. Always consult with a certified Veterans Service Officer (VSO) when filing a claim.

---

## 👤 Author

**Albert LaScola**  
📫 [https://bulwarkblack.com](https://bulwarkblack.com)  
💼 Cybersecurity + Veteran Advocacy

