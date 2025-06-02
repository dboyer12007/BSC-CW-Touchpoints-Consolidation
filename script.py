import os
import json
from datetime import datetime as dt
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------

BASE_PATH    = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER  = "test-data"
get_path     = lambda fn: os.path.join(BASE_PATH, DATA_FOLDER, fn)

def _strip(df: pd.DataFrame) -> pd.DataFrame:
    return df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

def _iso_fmt(date_str: str, time_str: str | None = None) -> str | None:
    if pd.isna(date_str):
        return None
    try:
        if time_str is None or pd.isna(time_str):
            stamp = pd.to_datetime(date_str, errors="coerce")
        else:
            stamp = pd.to_datetime(f"{date_str} {time_str}", errors="coerce")
        return stamp.strftime("%Y-%m-%dT%H:%M:%S") if not pd.isna(stamp) else None
    except Exception:
        return None

# ---------------------------------------------------------------------------
#  Load & clean the four source files
# ---------------------------------------------------------------------------

def clean_customer_info(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, skiprows=3)[
        ['CustomerName', 'ContactName', 'ContactTypeName', 'Textbox98']
    ]
    df.columns = ['customer_name_raw', 'contact_name', 'contact_type', 'contact_phone']
    df[['cust_last_name', 'cust_first_name']] = (
        df['customer_name_raw'].str.split(',', n=1, expand=True)
    )
    df = df.drop(columns=['customer_name_raw'])
    return _strip(df)

def clean_touchpoints(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns={
        'custFirstName': 'cust_first_name',
        'custLastName' : 'cust_last_name',
        'type'         : 'touchpoint_type',
        'dueDate'      : 'touchpoint_due'
    })
    return _strip(df)

def clean_schedule(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df[['cust_last_name', 'cust_first_name']] = (
        df['Customer'].str.split(',', n=1, expand=True)
    )
    df[['emp_last_name', 'emp_first_name']] = (
        df['Employee'].str.split(',', n=1, expand=True)
    )
    df[['Date', 'Start Time']] = df['Date'].astype(str).str.split(' ', n=1, expand=True)

    keep_cols = ['Date', 'Start Time', 'End Time', 'Status', 'Position',
                 'cust_first_name', 'cust_last_name',
                 'emp_first_name', 'emp_last_name']
    keep_cols = [col for col in keep_cols if col in df.columns]  # <- makes it safe
    return _strip(df[keep_cols])

def clean_employee_info(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, skiprows=3)
    df = df.drop_duplicates(subset="emEmployeeId")
    df['employee_name'] = df['firstName'].str.strip() + ' ' + df['lastName'].str.strip()
    df = df.rename(columns={
        'emEmployeeId'    : 'employee_id',
        'PhoneNumber'     : 'employee_phone',
        'StatusType'      : 'employee_status',
        'EmployeePosition': 'employee_position',
        'firstName'       : 'emp_first_name',
        'lastName'        : 'emp_last_name'
    })
    keep_cols = ['employee_id', 'employee_name', 'employee_phone',
                 'employee_status', 'employee_position',
                 'emp_first_name', 'emp_last_name']
    return _strip(df[keep_cols])

# ---------------------------------------------------------------------------
#  Load CSVs
# ---------------------------------------------------------------------------

customer_df  = clean_customer_info(get_path("customer_info.csv"))
touch_df     = clean_touchpoints   (get_path("touchpoints.csv"))
schedule_df  = clean_schedule     (get_path("schedule.csv"))
employee_df  = clean_employee_info(get_path("employee_info.csv"))

# ---------------------------------------------------------------------------
#  Merge everything
# ---------------------------------------------------------------------------

schedule_w_emp = schedule_df.merge(
    employee_df,
    on=['emp_first_name', 'emp_last_name'],
    how='left'
)

merged = (
    touch_df
        .merge(customer_df, on=['cust_first_name', 'cust_last_name'], how='left')
        .merge(schedule_w_emp, on=['cust_first_name', 'cust_last_name'], how='left')
)

merged['customer_name'] = (
    merged['cust_first_name'].str.strip() + ' ' + merged['cust_last_name'].str.strip()
)
merged = merged.rename(columns={'Status': 'schedule_status'})

merged = merged.drop_duplicates(subset=[
    'customer_name', 'employee_name', 'employee_phone',
    'Date', 'Start Time', 'End Time',
    'schedule_status', 'employee_position'
])

# ---------------------------------------------------------------------------
#  Build JSON structure
# ---------------------------------------------------------------------------

VALID_CONTACTS = {'responsible contact', 'referral'}

records = []
for cust_name, grp in merged.groupby('customer_name', dropna=False):
    first               = grp.iloc[0]
    touchpoint_type_val = first['touchpoint_type']
    touchpoint_due_val  = first['touchpoint_due']

    contacts_df = (
        grp[['contact_name', 'contact_type', 'contact_phone']]
        .dropna(subset=['contact_name'])
    )
    contacts_df = contacts_df[
        contacts_df['contact_type'].str.lower().isin(VALID_CONTACTS)
    ].drop_duplicates()

    contacts = [
        {
            "name" : row['contact_name'],
            "type" : row['contact_type'],
            "phone": None if pd.isna(row['contact_phone']) else row['contact_phone']
        }
        for _, row in contacts_df.iterrows()
    ]

    employees = []
    for (ename, ephone), egrp in grp.groupby(['employee_name', 'employee_phone'], dropna=False):
        if pd.isna(ename):
            continue

        emp_block = {
            "name"    : ename,
            "phone"   : None if pd.isna(ephone) else ephone,
            "shifts"  : []
        }

        for _, srow in egrp.iterrows():
            start_iso = _iso_fmt(srow['Date'],        srow['Start Time'])
            end_iso   = _iso_fmt(srow['End Time'])    # End Time already contains date+time

            emp_block["shifts"].append({
                "position"  : srow['employee_position'],
                "status"    : srow['schedule_status'],
                "startTime" : start_iso,
                "endTime"   : end_iso,
            })

        employees.append(emp_block)

    records.append({
        "name"      : cust_name,
        "type"      : touchpoint_type_val,
        "dueDate"   : touchpoint_due_val,
        "contacts"  : contacts,
        "employees" : employees,
    })

# ---------------------------------------------------------------------------
#  Save to JSON
# ---------------------------------------------------------------------------

def _np2py(obj):
    return obj.item() if isinstance(obj, np.generic) else obj

json_ready = json.loads(json.dumps(records, default=_np2py))
out_path   = get_path("customers_grouped.json")

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(json_ready, f, indent=2)

print(f"✅ JSON exported to {out_path}")
