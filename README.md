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


## Data Disclaimer

All data included in this repository is sample data created for development and demonstration purposes only.  
No real patient or employee information is included. Any names or details used are entirely fictitious.  
This project complies with HIPAA and privacy standards.



## Example Output (JSON)

Below is a simplified example of what the final `customers_grouped.json` structure looks like:

```json
[
  {
    "name": "John Doe",
    "type": "Responsible Contact",
    "dueDate": "2024-12-01",
    "contacts": [
      {
        "name": "Jane Doe",
        "type": "Responsible Contact",
        "phone": "555-123-4567"
      }
    ],
    "employees": [
      {
        "name": "Alice Smith",
        "phone": "555-987-6543",
        "shifts": [
          {
            "position": "Nurse",
            "status": "Confirmed",
            "startTime": "2024-12-01T09:00:00",
            "endTime": "2024-12-01T12:00:00"
          }
        ]
      }
    ]
  }
]
```
