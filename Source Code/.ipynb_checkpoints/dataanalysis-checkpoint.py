#!/usr/bin/env python
# coding: utf-8

# In[1]:


# EDA libraries 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv('../datasets/synthetic_transactions_clean.csv')

# Quick sanity checks for dataframe
print("Shape:", df.shape)
print("\nColumns:\n", df.columns.tolist())

# Show first 5 rows
df.head()


# In[26]:


# grouping by merchants to find top 5 merchants by average amount spent
merchant_avg = (
    df
    .groupby("merchant", as_index=False)["amount"]
    .mean()
    .sort_values(by="amount", ascending=False)
)

merchant_avg.head()


# In[28]:


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

# In[30]:


# same thing but group by total
merchant_total = (
    df
    .groupby("merchant", as_index=False)["amount"]
    .sum()
    .sort_values(by="amount", ascending=False)
)

merchant_total.head()


# Top Spender in total is Instacart

# In[32]:


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


# In[80]:


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

    print("\n--- Top 5 Merchants by AVERAGE Amount ---")
    print(merchant_avg.head(5))

    print("\n--- Top 5 Merchants by TOTAL Amount ---")
    print(merchant_total.head(5))

    # Optional: quick plots
    choice = input("\nShow quick amount / merchant plots? (y/n): ").strip().lower()

    if choice == "y":
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
    else:
        print("Skipping plots.")

    print("\nAnalysis complete.\n")


# In[82]:


analysis_demo()


# In[ ]:




