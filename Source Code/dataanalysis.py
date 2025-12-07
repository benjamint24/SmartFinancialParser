#!/usr/bin/env python
# coding: utf-8

# In[140]:


# EDA libraries 
import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns


df = pd.read_csv('../datasets/synthetic_transactions_clean.csv')

# Quick sanity checks for dataframe
#print("Shape:", df.shape)
#print("\nColumns:\n", df.columns.tolist())

# Show first 5 rows
df.head()


# In[141]:


# grouping by merchants to find top 5 merchants by average amount spent
merchant_avg = (
    df
    .groupby("merchant", as_index=False)["amount"]
    .mean()
    .sort_values(by="amount", ascending=False)
)

merchant_avg.head()


# In[142]:


plt.figure(figsize=(14, 6))

sns.barplot(
    data=merchant_avg,
    x="merchant",
    y="amount"
)

plt.xticks(rotation=45, ha="right")
plt.xlabel("Merchant")
plt.ylabel("Total Transaction Amount")
plt.title("Total Transaction Amount by Merchant")


# Top Spender on average is LOWE'S

# In[144]:


# same thing but group by total
merchant_total = (
    df
    .groupby("merchant", as_index=False)["amount"]
    .sum()
    .sort_values(by="amount", ascending=False)
)

merchant_total.head()


# Top Spender in total is Instacart

# In[147]:


plt.figure(figsize=(14, 6))

sns.barplot(
    data=merchant_total,
    x="merchant",
    y="amount"
)

plt.xticks(rotation=45, ha="right")
plt.xlabel("Merchant")
plt.ylabel("Total Transaction Amount")
plt.title("Total Transaction Amount by Merchant")


# In[158]:


CLEAN_FILE = "../datasets/synthetic_transactions_clean.csv"


def analysis_demo():
    print("\n=== TRANSACTION ANALYSIS DEMO ===\n")

    # Load cleaned data
    try:
        df = pd.read_csv(CLEAN_FILE)
    except FileNotFoundError:
        print(f"Could not find cleaned file at: {CLEAN_FILE}")
        print("Run the cleaning step first.")
        return

    # Quick sanity checks
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print("\nColumns:", df.columns.tolist())

    print("\n--- Data Preview (first 5 rows) ---")
    print(df.head())

    # Top merchants by average amount
    merchant_avg = (
        df
        .groupby("merchant", as_index=False)["amount"]
        .mean()
        .sort_values(by="amount", ascending=False)
    )

    # Top merchants by total amount
    merchant_total = (
        df
        .groupby("merchant", as_index=False)["amount"]
        .sum()
        .sort_values(by="amount", ascending=False)
    )

    top_avg = merchant_avg.iloc[0]
    top_total = merchant_total.iloc[0]

    print("\nMost expensive merchant on average: ")
    print(top_avg["merchant"])

    print("Most expensive merchant in total: ")
    print(top_total["merchant"])

    print("\n--- Top 5 Merchants by AVERAGE Amount ---")
    print(merchant_avg.head(5))

    print("\n--- Top 5 Merchants by TOTAL Amount ---")
    print(merchant_total.head(5))

    print("\nAnalysis complete.\n")


# In[160]:


if __name__ == "__main__":
    analysis_demo()


# In[ ]:





# In[ ]:





# In[ ]:




