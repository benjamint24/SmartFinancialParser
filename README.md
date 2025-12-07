# Smart Financial Transaction Parser

This project is a data pipeline that generates, cleans, and analyzes financial transaction data. 

## How to Run the Project (Terminal)
- Clone this resposity to wherever you want
- Navigate to where the project is cloned to in your terminal
- From the project root directory: cd Source Code
- In the Source Code foler: python pipeline.py

You will be guided through:
1. Data Creation – generates synthetic transactions with user-entered amount of rows
2. Data Cleaning – normalizes dates, merchants, and amounts
3. Data Analysis – outputs analytics and summaries of top merchant and table for top 5 by average and total

At the end, you will be prompted to run the entire pipeline again without restarting the program if you wish.

## Screenshots

### Libraries used
- Pandas: used for CSV data manipulation, validation, and supplemental inspection outside the core pipeline logic on developer side.
- Time: for delay in pipeline
- CSV: to create csv files
- RE: for regular expression (regex) handling
- Datetime: for date formatting and additional functions (e.g. timedelta)
- Random: to introduce randomness in data creation
- Matplotlib & Seaborn: data anlysis tools not used in the pipeline but for own exploration


## Methodology

### Data Creation (

### Data Cleaning

### Data Analysis


## Organization of Files

SmartFinancialParser/  
  
  Source Code/  
    pipeline.py – Main controller script that runs the full system  
    pipeline.ipynb – Notebook version of the full pipeline execution  
    datacreation.py – Handles synthetic data generation  
    datacreation.ipynb – Notebook version of synthetic data generation  
    datacleaning.py – Handles normalization and cleaning logic  
    datacleaning.ipynb – Notebook version of data cleaning and validation  
    dataanalysis.py – Handles analysis and reporting  
    dataanalysis.ipynb – Notebook version of exploratory data analysis and validation  
  
  datasets/  
    synthetic_transactions.csv – Raw generated dataset  
    synthetic_transactions_clean.csv – Cleaned output dataset  

  
    
  README.md – Project documentation  


## Design Principles
- 

## Future Improvements
- 

## Author
Benjamin Tran  
Computer Science
