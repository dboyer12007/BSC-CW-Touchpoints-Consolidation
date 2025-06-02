# BSC-CW Touchpoints Consolidation

This Python project was developed under contract for **BrightStar Care – Cuyahoga West**. It consolidates customer, employee, and schedule data from multiple CSV sources into a single structured JSON file. The output enables staff to quickly access all necessary information for touchpoint calls, eliminating the need to manually reference multiple spreadsheets.

## Overview

The tool was designed to support a real-world workflow in which employees previously had to gather information from four separate CSVs. This script automates the entire process:

- Cleans and standardizes raw input files  
- Merges data into a unified structure  
- Outputs a nested JSON file that can be reused or imported into other systems  

## Input Files

All input CSVs are placed in the `test-data/` directory:

- `customer_info.csv`  
- `employee_info.csv`  
- `schedule.csv`  
- `touchpoints.csv`  

Each file contributes unique and overlapping data necessary for customer touchpoint planning.

## Output File

- `customers_grouped.json`

A structured JSON file that includes:

- Customer name and contact information  
- Touchpoint type (e.g., Responsible Contact, Referral)  
- Assigned employees with phone numbers, positions, and shift times  
- Schedule status and other context for outreach preparation  

## How to Run

1. Place all required CSVs in the `test-data/` folder  
2. Run the script from the root directory:  
   ```bash
   python script.py
   ```  
3. The final output will be saved as `customers_grouped.json`

## Technologies Used

- Python 3  
- pandas  
- datetime  
- json  
- os (for file path handling)  

## Why It Matters

This project was created to reduce manual effort and prevent errors in daily operations. It is fully reusable — allowing staff to update their outreach dataset by simply replacing the CSVs and rerunning the script.
