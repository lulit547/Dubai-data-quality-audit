"""
Generates a synthetic 'dirty' e-commerce orders dataset for Dubai-based retailer.
Simulates realistic data quality issues: missing values, duplicates,
inconsistent formatting, invalid dates, bad emails, outliers.
"""
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

N = 5000

first_names = ["Ahmed","Fatima","Mohammed","Aisha","Ali","Sara","Omar","Layla","Khalid","Noor",
               "Rashid","Mariam","Yousef","Huda","Hassan","Zainab","Salem","Reem","Tariq","Amina"]
last_names = ["Al Maktoum","Al Falasi","Khan","Ahmed","Hassan","Ibrahim","Rahman","Al Ali",
              "Al Suwaidi","Malik","Sheikh","Al Rashid","Patel","Nasser","Al Amiri"]

cities_clean = ["Dubai","Abu Dhabi","Sharjah","Ajman","Fujairah","Ras Al Khaimah"]
cities_messy = ["dubai","DUBAI","Dubai ","Abu dhabi","abu dhabi","AbuDhabi","sharjah",
                "Sharjah ","ajman","Ras al Khaimah","RAK","Fujeirah"]

categories = ["Electronics","Fashion","Home & Kitchen","Beauty","Sports","Groceries","Toys","Books"]
payment_methods = ["Credit Card","Debit Card","Cash on Delivery","Apple Pay","credit card","COD","CC"]

rows = []
for i in range(1, N + 1):
    order_id = f"ORD{i:06d}"
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    customer_id = f"CUST{random.randint(1, 1800):05d}"

    # email - sometimes malformed or missing
    r = random.random()
    if r < 0.06:
        email = None
    elif r < 0.10:
        email = f"{fname.lower()}.{lname.lower().replace(' ','')}@gmail"  # missing .com
    elif r < 0.13:
        email = f"{fname.lower()}{lname.lower().replace(' ','')}gmail.com"  # missing @
    else:
        domain = random.choice(["gmail.com","yahoo.com","hotmail.com","outlook.com"])
        email = f"{fname.lower()}.{lname.lower().replace(' ','')}{random.randint(1,99)}@{domain}"

    city = random.choice(cities_messy) if random.random() < 0.35 else random.choice(cities_clean)

    order_date = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 545))
    # ship date sometimes before order date (bad data) or missing
    r2 = random.random()
    if r2 < 0.04:
        ship_date = order_date - timedelta(days=random.randint(1, 5))  # invalid: ships before order
    elif r2 < 0.09:
        ship_date = None
    else:
        ship_date = order_date + timedelta(days=random.randint(1, 10))

    category = random.choice(categories)
    price = round(np.random.lognormal(mean=4.2, sigma=1.0), 2)
    # inject extreme outliers
    if random.random() < 0.01:
        price = round(price * random.choice([50, 100, -1]), 2)

    quantity = random.choice([1,1,1,2,2,3,4,5])
    payment = random.choice(payment_methods)

    phone = f"+971 5{random.randint(0,9)} {random.randint(1000000,9999999)}"
    if random.random() < 0.05:
        phone = f"05{random.randint(0,9)}{random.randint(1000000,9999999)}"  # inconsistent format

    rows.append({
        "order_id": order_id,
        "customer_id": customer_id,
        "customer_name": f"{fname} {lname}" if random.random() > 0.03 else f"{fname}  {lname} ",
        "email": email,
        "phone": phone,
        "city": city,
        "order_date": order_date.strftime("%Y-%m-%d") if random.random() > 0.15 else order_date.strftime("%d/%m/%Y"),
        "ship_date": ship_date.strftime("%Y-%m-%d") if ship_date else None,
        "category": category,
        "unit_price_aed": price if random.random() > 0.05 else None,
        "quantity": quantity,
        "payment_method": payment,
    })

df = pd.DataFrame(rows)

# Inject exact duplicate rows
dupes = df.sample(150, random_state=1)
df = pd.concat([df, dupes], ignore_index=True)

# Inject duplicate order_ids with different data (a nastier duplicate type)
near_dupes = df.sample(60, random_state=2).copy()
near_dupes["order_id"] = near_dupes["order_id"]
near_dupes["quantity"] = near_dupes["quantity"] + 1
df = pd.concat([df, near_dupes], ignore_index=True)

df = df.sample(frac=1, random_state=3).reset_index(drop=True)
df.to_csv("raw_orders.csv", index=False)
print(f"Generated {len(df)} rows -> raw_orders.csv")
print(df.head())
