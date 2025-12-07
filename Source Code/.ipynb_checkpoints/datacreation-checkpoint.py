#!/usr/bin/env python
# coding: utf-8

# In[116]:


import csv
import random
from datetime import date, timedelta 


# global variables (rows, start/end date, output path)

START_DATE = date(2019, 1, 1)
END_DATE = date(2025, 12, 31)
OUTPUT_FILE = OUTPUT_FILE = "../datasets/synthetic_transactions.csv"

# Helper Functions
# 1. Date helpers
# 2. Merchant helpers
# 3. Price helpers
# -----------------------

# generates a random date using timedelta
def random_date() -> date:
    delta_days = (END_DATE - START_DATE).days
    offset = random.randint(0, delta_days)
    return START_DATE + timedelta(days=offset)

# accounts for day suffixes
def day_suffix(day: int) -> str:
    if 11 <= day <= 13:
        return "th"
    last = day % 10
    if last == 1:
        return "st"
    if last == 2:
        return "nd"
    if last == 3:
        return "rd"
    return "th"

# randomize date formats, creates a bunch of formats for the same date and then picks one at random
def format_date_mixed(d: date) -> str:
    """
    All options also mix up 0-padding and no padding using random to split(e.g. 2025-08-07 and 2025-8-7)
    Random formats include:
    YYYY-MM-DD
    MM/DD/YYYY
    MMM DD YYYY (MMM is month name abbreviation, e.g., Jan 21 2024)
    MMM Dth YY (Dth is day with suffix, e.g., "Oct 23rd 23"))
    D-M-YY
    DD-MM-YY
    DD MMM YY
    D MMM YYY  
    """

    #split up date into year, month, and day and formats
    year_full = d.year
    year_short = year_full % 100
    month = d.month
    day = d.day
    month_names_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    mmm = month_names_short[month - 1]
    suffix = day_suffix(day)

    formats = []

    # YYYY-MM-DD
    if random.random() < 0.5:
        #padded
        formats.append(f"{year_full}-{month:02d}-{day:02d}")
    else:
        #not padded
        formats.append(f"{year_full}-{month}-{day}")

    # MM/DD/YYYY or M/D/YYYY
    if random.random() < 0.5:
        #padded
        formats.append(f"{month:02d}/{day:02d}/{year_full}")
    else:
        #not padded
        formats.append(f"{month}/{day}/{year_full}")

    # MMM DD YYYY (month name abbreviation)
    if random.random() < 0.5:
        #padded
        formats.append(f"{mmm} {day:02d} {year_full}")
    else:
        #not padded
        formats.append(f"{mmm} {day} {year_full}")

    # MMM Dth YY (month name abbreviation and data suffix, and short year format)
    formats.append(f"{mmm} {day}{suffix} {year_short:02d}")

    # D-M-YY or DD-MM-YY (short format year)
    if random.random() < 0.5:
        #not padded
        formats.append(f"{day}-{month}-{year_short:02d}")
    else:
        #padded
        formats.append(f"{day:02d}-{month:02d}-{year_short:02d}")

    # DD MMM YY or D MMM YYYY
    
    if random.random() < 0.5:
        formats.append(f"{day} {mmm} {year_short:02d}")
    else:
        formats.append(f"{day} {mmm} {year_full}")

    #pick a random choice from formats as the final 
    return random.choice(formats)


# 19 different Merchants 2-4 different names for each generation
# Restaurant, Retail, and Service all have unique values, the other 16 categories should all map to the key, total should be 27 unique
# -----------------------
BASE_MERCHANTS = {
    "UBER": ["UBER", "Uber", "Uber Technologies", "UBER EATS", "UBER *TRIP"],
    "STARBUCKS": ["Starbucks", "STARBUCKS", "Starbucks Coffee"],
    "AMAZON": ["Amazon", "AMZN", "Amazon Marketplace"],
    "WALMART": ["Walmart", "WAL-MART", "Walmart Supercenter"],
    "TARGET": ["Target", "TARGET", "Target Store"],
    "MCDONALDS": ["McDonalds", "McDonald's", "MCD"],
    "SHELL": ["Shell", "Shell Oil", "SHELL GAS"],
    "LYFT": ["Lyft", "LYFT RIDE"],
    "SPOTIFY": ["Spotify", "SPOTIFY", "Spotify Pmnt"],
    "NETFLIX": ["Netflix", "NETFLIX", "Netflix.com"],
    "APPLE": ["Apple", "APPLE.COM/BILL", "Apple Services"],
    "GOOGLE": ["Google", "GOOGLE *SERVICES", "Google Play"],
    "DOORDASH": ["DoorDash", "DOORDASH", "DOORDASH*ORDER"],
    "INSTACART": ["Instacart", "INSTACART"],
    "AIRBNB": ["Airbnb", "AIRBNB", "AIRBNB PAY"],
    "COSTCO": ["Costco", "COSTCO WHOLESALE"],
    "RESTAURANT": ["Olive Garden", "Chipotle", "Panda Express", "Sushi House"],
    "RETAIL": ["Best Buy", "Home Depot", "LOWE'S", "Macy's"],
    "SERVICE": ["City Utilities", "Gym Membership", "Car Wash Pro"],
}

# randomization for merchant names (upper/lower/title/mixed case)
def random_case_variant(s: str) -> str:
    # weights: upper=30%, lower=30%, title=35%, mixed=5%, mixed shouldn't be to common
    mode = random.choices(
        ["upper", "lower", "title", "mixed"],
        weights=[0.3, 0.3, 0.35, 0.05],
        k=1
    )[0]

    if mode == "upper":
        return s.upper()
    if mode == "lower":
        return s.lower()
    if mode == "title":
        return s.title()

    # mixed case
    chars = []
    for ch in s:
        if ch.isalpha():
            chars.append(ch.upper() if random.random() < 0.5 else ch.lower())
        else:
            chars.append(ch)
    return "".join(chars)

# add one space with a small chance and two spaces with an even smaller chance
def maybe_add_spaces(s: str) -> str:
   
    # leading/trailing spaces (small chance of .2)
    if random.random() < 0.2:
        s = " " + s
    if random.random() < 0.2:
        s = s + " "
    # extra internal spaces randomly
    if " " in s and random.random() < 0.3:
        s = s.replace(" ", "  ")
    return s

# adds a prefix and/or suffix with a chance
def maybe_add_prefix_suffix(s: str) -> str:
    #has empty quotes so that it doesn't always add a prefix
    prefixes = [""] * 20 + ["#", "PAYPAL*", "SQ*", "UBER-", "POS ", "ACH "]
    suffixes = [""] * 20 + [" INC", " LTD", ".COM", " (ONLINE)", " [AUTO]", " *PMT"]
    s = random.choice(prefixes) + s + random.choice(suffixes)
    return s

# adds typo (insert/delete) only only if long enough string and with 10% chance
def maybe_add_typos(s: str) -> str:
    
    if len(s) < 4 or random.random() > 0.1:
        return s

    #pick position and typo type
    s_list = list(s)
    idx = random.randrange(len(s_list))
    operation = random.choice(["delete", "replace"])

    if operation == "delete":
        del s_list[idx]
    else:  # replace
        s_list[idx] = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
    
    return "".join(s_list)

# adds special character noise wiht a 20% chance
def maybe_add_regex_noise(s: str) -> str:

    if random.random() > 0.2:
        return s

    # common special characters/extra phrases and determine placement
    noise_tokens = [".*", "?", "+", "()", "[]", "[TRIP]", "(EATS)", ".*UBR"]
    token = random.choice(noise_tokens)

    #put the token at either the beginning or end of the string
    if random.random() < 0.5:
        return token + " " + s
    else:
        return s + " " + token

# putting all merchant helpers together, maybes happen with a chance (already implemented within maybes)
def random_merchant() -> str:
    # Choose a merchant family and base name
    family = random.choice(list(BASE_MERCHANTS.keys()))
    base_name = random.choice(BASE_MERCHANTS[family])

    # Apply transformations
    s = base_name
    s = random_case_variant(s)
    s = maybe_add_typos(s)
    s = maybe_add_prefix_suffix(s)
    s = maybe_add_regex_noise(s)
    s = maybe_add_spaces(s)

    return s


# Amount generation
# -----------------------

# one helper for amount from 1 to 2500, occasional refunds, occasional round numbers, and formatted by itself, with $ or USD, and occaisional spaces
def format_amount_mixed() -> str:
    
    #generate base amt
    base = random.uniform(1, 2500)

    #for refunds
    if random.random() < 0.05:
        base = -base

    # 20% whole, rest have decimal, half have decimal, half don't
    
    if random.random() < 0.2:
        whole = int(round(base))
        if random.random() < 0.5:
            #yes comma
            num_str = f"{whole:,}" 
        else:
            #no comma
            num_str = str(whole)
    else:
        # with decimals
        if random.random() < 0.5:
            #no comma
            num_str = f"{base:.2f}"
        else:
            #yes comma
            num_str = f"{base:,.2f}"

    # Randomly choose a currency style
    style = random.choice(["plain", "dollar", "usd_before", "usd_after"])

    #plain
    if style == "plain":
        s = num_str
    #dollar sign
    elif style == "dollar":
        #no space
        if random.random() < 0.5:
            s = "$" + num_str
        #yes space
        else:
            s = "$ " + num_str
    #with 'USD' before
    elif style == "usd_before":
        #yes space
        if random.random() < 0.5:
            s = "USD " + num_str
        #no space
        else:
            s = "USD" + num_str
    #with 'USD' after
    else: 
        #yes space
        if random.random() < 0.5:
            s = num_str + " USD"
        #no space
        else:
            s = num_str + "USD"

    #  with small chance add random leading/trailing spaces
    if random.random() < 0.1:
        s = " " + s
    if random.random() < 0.1:
        s = s + " "

    return s



# Main CSV Generation, bringing it all together
def main(num_rows: int = 1000):
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # header row
        writer.writerow(["date", "merchant", "amount"])

        for _ in range(num_rows):
            d = random_date()
            date_str = format_date_mixed(d)
            merchant_str = random_merchant()
            amount_str = format_amount_mixed()

            writer.writerow([date_str, merchant_str, amount_str])

    print(f"Synthetic, error-filled CSV generated successfully with {num_rows} rows.")

def creation_demo():
    print("Enter the amount of rows of messy data to generate:")
    
    try:
        num_rows = int(input(">> "))

        if num_rows <= 0:
            print("Row count must be a positive integer.")

        main(num_rows)  
        return True

    except ValueError:
        print("Invalid input. Please enter a valid integer.")
        return False
        
if __name__ == "__main__":
    main()


# In[104]:


#quick check
import pandas as pd

df = pd.read_csv('../datasets/synthetic_transactions.csv')
df.head(50)


# In[ ]:





# In[ ]:





# In[ ]:




