#!/usr/bin/env python
# coding: utf-8

# In[268]:


import csv
import re
from datetime import datetime
from typing import List, Dict, Optional

# input/output files
INPUT_FILE = "../datasets/synthetic_transactions.csv"
OUTPUT_FILE = "../datasets/synthetic_transactions_clean.csv"

# merchants match my base merchants from data creation
BASE_MERCHANTS = {
    #first 16 should all map to the key
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
    
    #last three should just map to the name in the end
    
    # Restaurants
    "OLIVE_GARDEN": ["Olive Garden"],
    "CHIPOTLE": ["Chipotle"],
    "PANDA_EXPRESS": ["Panda Express"],
    "SUSHI_HOUSE": ["Sushi House"],

    # Retail
    "BEST_BUY": ["Best Buy"],
    "HOME_DEPOT": ["Home Depot"],
    "LOWES": ["LOWE'S"],
    "MACYS": ["Macy's"],

    # Service
    "CITY_UTILITIES": ["City Utilities"],
    "GYM_MEMBERSHIP": ["Gym Membership"],
    "CAR_WASH_PRO": ["Car Wash Pro"],
}


# Date parsing and normalization
# -----------------------------

DATE_PATTERNS = [
    "%Y-%m-%d",   # 2021-6-7 or 2021-06-07
    "%m/%d/%Y",   # 6/7/2021 or 06/07/2021
    "%b %d %Y",   # Jun 7 2021 or Jun 07 2021
    "%d-%m-%y",   # 7-6-21 or 07-06-21
    "%d %b %y",   # 7 Jun 21
    "%d %b %Y",   # 7 Jun 2021
]
 
#regex using re that takes care of all MMM DD+suffix YY formats 
#HAS to have (in order)
       # -starting (^) with three alphabetic characters mixed case allowed : (?P<mon>[A-Za-z]{3})
       # -1 more more spaces : \s+
       # -date with one or two digits: (?P<day>\d{1,2})
       # -required suffix right after
       # : (st|nd|rd|th)
       #-1 more more spaces : \s+
       # -year with 2 digits : (?P<year>\d{2})
       # -NOTHING after: $
'''
    Example cases:
        Jan 1st 21
        Oct 23rd 19
        Feb 07th 05
        mAr 3rd 24
        Apr   9th    17
'''   
_suffix_date_regex = re.compile(
    
    r"^(?P<mon>[A-Za-z]{3})\s+(?P<day>\d{1,2})(st|nd|rd|th)\s+(?P<year>\d{2})$"
)

# parse data with with datetime's dt which can automatically format all the other formats except for MMM Dth YY
def parse_date(raw: str) -> Optional[str]:
    s = str(raw).strip()

    # Try all direct patterns first
    for pattern in DATE_PATTERNS:
        try:
            dt = datetime.strptime(s, pattern)
            return dt.date().isoformat()  # YYYY-MM-DD
        except ValueError:
            continue

    # use regex to handle mmm dth yy

    #match handles different starts
    m = _suffix_date_regex.match(s)
    if m:
        #convert to valid datetime format to get ready to convert
        mon_str = m.group("mon")
        day = int(m.group("day"))
        year_short = int(m.group("year"))

        year_full = 2000 + year_short

        #convert to datetime
        try:
            dt = datetime.strptime(f"{mon_str} {day} {year_full}", "%b %d %Y")
            return dt.date().isoformat()
        except ValueError:
            return None

    return None



# Merchant normalization (27 uniques)
# -------------------------------------

# Canonical form for matching: uppercase and strip non-alphanumeric
def _canonical_string(s: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", s.upper())


# related to these should collpase to one of these 16
BRAND_KEYS = {
    "UBER",
    "STARBUCKS",
    "AMAZON",
    "WALMART",
    "TARGET",
    "MCDONALDS",
    "SHELL",
    "LYFT",
    "SPOTIFY",
    "NETFLIX",
    "APPLE",
    "GOOGLE",
    "DOORDASH",
    "INSTACART",
    "AIRBNB",
    "COSTCO",
}

# Build (canonical_base, canonical_output) pairs:
# - If family in BRAND_KEYS -> output key
# - IF restaurants/retail/service -> output original name
# CANONICAL_BASES = list of {OUTPUT AFTER CLEANING: KEY NAME}
CANONICAL_BASES = []
for family, names in BASE_MERCHANTS.items():
    if family in BRAND_KEYS:
        canonical_output = family          
    else:
        canonical_output = names[0]      

    for base in names:
        canon = _canonical_string(base)
        if not canon:
            continue
        CANONICAL_BASES.append((canon, canonical_output.upper()))

# Matches based on spelling errors using edit distance algorithm
def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    #list of counting integers to length of b, updates so it shows number of edits needed at each stage in word b
    prev = list(range(len(b) + 1))
    #loop to get min changes to turn a into b
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            ins = cur[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (ca != cb)
            #whichever takes the shortest
            cur.append(min(ins, delete, sub))
        prev = cur
    #return final index at the end of b
    return prev[-1]


def clean_merchant(raw: str) -> str:
    """
    Returns cleaned merchant name.
    If it cannot be mapped, returns the string "ERROR".
    """
   
    s = str(raw).strip()
    
    if not s:
        return "ERROR"

    #uses cleaner regex function from earlier
    canon_input = _canonical_string(s)

    if not canon_input:
        return "ERROR"

    # first filter check for matches that have no spelling errors by handling extra characters and finding best match
    best_match = None
    best_len = 0
    for canon_base, canonical_output in CANONICAL_BASES:
        #checks if input contains one of the bases, only makes best match if has more matching characters than pervious best match
        if canon_base in canon_input and len(canon_base) > best_len:
            best_len = len(canon_base)
            best_match = canonical_output
    
    # returns if found valid match
    if best_match is not None:
        return best_match

    # second fiter accounts for spelling errors using previous levenshtein filter using the same length matching as filter 1
    # matches when theres a very small difference due to spellingthere's
    best_dist = 10**9
    best = None
    for canon_base, canonical_output in CANONICAL_BASES:
        # gets number of matching, take canonical_output of smallest dist as small dist means least edits (likely 1 or 2 due to spelling errors)
        dist = levenshtein(canon_input, canon_base)
        if dist < best_dist:
            best_dist = dist
            best = canonical_output

    # should return at this point if not at the first filter
    if best is not None:
        return best

    # Final fallback — nothing matched
    return "ERROR"



    
# Amount normalization, one functions
# ---------------------

# converts messy amounts and returns into 2 decimal format
def parse_amount(raw: str) -> Optional[str]:

    #leading and trailing spaces
    s = str(raw).strip()


    # Remove USD (rusing regex to match usd at beginning end and with mixed cases), $, and commas
    s = re.sub(r"(?i)usd", "", s)
    s = s.replace("$", "").replace(",", "")
    s = s.strip()

    #convert to float with two decimals
    return f"{float(s):.2f}" if s else None


# Main cleaning , bringing it all together
# --------------------------

def clean_csv() -> Dict[str, object]:
    #keepign track of rows and errors
    cleaned_rows: List[Dict[str, str]] = []
    date_errors = 0
    amount_errors = 0
    merchant_unmapped = 0
    total_rows = 0

    # create and fill new csv with clean values
    with open(INPUT_FILE, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_rows += 1

            # grabbing messy values
            raw_date = row.get("date", "")
            raw_merchant = row.get("merchant", "")
            raw_amount = row.get("amount", "")
            
            # cleaning values
            clean_date = parse_date(raw_date)
            clean_amount = parse_amount(raw_amount)
            clean_merchant_val = clean_merchant(raw_merchant)

            # error catching
            if clean_date is None:
                date_errors += 1
                continue

            if clean_amount is None:
                amount_errors += 1
                continue

            if clean_merchant_val == "ERROR":
                merchant_unmapped += 1

            # adding clean data to dataset
            cleaned_rows.append(
                {
                    "date": clean_date,
                    "merchant": clean_merchant_val,
                    "amount": clean_amount,
                }
            )

    # Write cleaned CSV
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=["date", "merchant", "amount"])
        writer.writeheader()
        writer.writerows(cleaned_rows)

    return {
        "cleaned_rows": cleaned_rows,
        "total_rows": total_rows,
        "date_errors": date_errors,
        "amount_errors": amount_errors,
        "merchant_unmapped": merchant_unmapped,
    }


def main():
    #run clean_csv and print out statistics
    result = clean_csv()

    cleaned_rows = result["cleaned_rows"]
    total_rows = result["total_rows"]
    date_errors = result["date_errors"]
    amount_errors = result["amount_errors"]
    merchant_unmapped = result["merchant_unmapped"]

    print(f"Total raw rows:       {total_rows}")
    print(f"Rows kept:            {len(cleaned_rows)}")
    print(f"Date parse errors:    {date_errors}")
    print(f"Amount parse errors:  {amount_errors}")
    print(f"Unmapped merchants:   {merchant_unmapped}")

    unique_merchants = sorted(set(r["merchant"] for r in cleaned_rows))
    print(f"Unique merchants ({len(unique_merchants)}):")
    for m in unique_merchants:
        print("  ", m)

def cleaning_demo():
    print("Now, we can clean the raw synthetic transactions file.")
    print(f"Input file:  {INPUT_FILE}")
    print(f"Output file: {OUTPUT_FILE}")
    print("\nProceed with cleaning? (y/n)")

    choice = input(">> ").strip().lower()

    if choice == "y":
        result = clean_csv()

        cleaned_rows = result["cleaned_rows"]
        total_rows = result["total_rows"]
        date_errors = result["date_errors"]
        amount_errors = result["amount_errors"]
        merchant_unmapped = result["merchant_unmapped"]
    
        print(f"Total raw rows:       {total_rows}")
        print(f"Rows kept:            {len(cleaned_rows)}")
        print(f"Date parse errors:    {date_errors}")
        print(f"Amount parse errors:  {amount_errors}")
        print(f"Unmapped merchants:   {merchant_unmapped}")
        
        print("Cleaning completed successfully.")
        return True
    else:
        print("Cleaning canceled, quitting program.")
        return False

    

if __name__ == "__main__":
    main()



# In[249]:


#sanity check
import pandas as pd

df = pd.read_csv(OUTPUT_FILE)
df.head()


# In[250]:


CANONICAL_BASES


# In[ ]:





# In[ ]:




