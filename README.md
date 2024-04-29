# VA-Disability-Calculator
Very simple and easy to use VA disability calculator

You can downlaod the executable for windows or run the code on your prefered OS. 

Separate values with a space and calculate Disability rating, that simple. It does not matter what order you enter the values for this application.

## How is the VA Disability Calculated
1. List of Disabilities: You start with a list of disabilities, each with its own percentage rating.
2. Sort Percentages: Order these percentages from highest to lowest.
3. Calculate Combined Disability:
- Start with the highest percentage.
- For each subsequent percentage, calculate the combined rating as follows:
  - Take the remaining percentage of "ability" left after accounting for the first disability. For example, if the first disability is rated at 40%, then 60% "ability" remains.
  - Multiply this remaining percentage by the next highest disability percentage.
  - Add the result to the previous disability rating to get the new combined disability rating.
4. Final Step: Continue this process down the list of disabilities. The final result is subtracted from 100% to find the total disability rating.

NOTE: Actual percentage is different from awarded percentage. For example if your actual percentage is 55% you will be awarded 60% but if it is 54% you will be awarded 50%. The VA rounds towards the nearest 10th.
