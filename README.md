# Smart Financial Transaction Parser

Welcome! This project is a data pipeline that generates, cleans, and analyzes financial transaction data. 

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

The messy raw dataset and the finalized cleaned dataset are both available in the `datasets/` directory as `synthetic_transactions.csv` and `synthetic_transactions_clean.csv`.


## Screenshots of Demo
<p align="center">
  <img src="https://github.com/user-attachments/assets/d4724ad5-18cd-48b5-9fd1-1e6f287b2cd7" width="480" />
</p>
<p align="center"><em>Demo Data Creation and Cleaning</em></p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/0078a24e-3cb6-4e59-862c-bc3f94d51886" width="480" />
</p>
<p align="center"><em>Demo Data Analysis</em></p>



### Libraries used
- Pandas: used for CSV data manipulation, validation, and supplemental inspection outside the core pipeline logic on developer side.
- Time: for delay in pipeline
- CSV: to create csv files
- RE: for regular expression (regex) handling
- Datetime: for date formatting and additional functions (e.g. timedelta)
- Random: to introduce randomness in data creation
- Matplotlib & Seaborn: data anlysis tools not used in the pipeline but for own exploration


## Code Structure

There are 4 main files: 
datacreation - creates messy data and saves it to a csv
datacleaning - cleans messy data from messy dataset and creates clean dataset
dataanalysis - does basic eda on clean dataset
pipeline - puts the first three into a cli demonstration

### Data Creation

This first file intentionally messy transactions CSV. It uses helper functions for dates, merchants, and amounts, and a main generator to write the output file.

#### Helper Methods

**Date Helpers**
- `random_date() -> date`  
  Generates a random date between `START_DATE` and `END_DATE` using a random day offset.
- `day_suffix(day: int) -> str`  
  Computes the correct ordinal suffix for a day (e.g., `1 -> "st"`, `2 -> "nd"`, `3 -> "rd"`, `4 -> "th"`, including special handling for special cases 11–13).
- `format_date_mixed(d: date) -> str`  
  Converts a `date` object into one of many randomized string formats (e.g., `YYYY-MM-DD`, `MM/DD/YYYY`, `MMM DD YYYY`, `MMM Dth YY`, `D-M-YY`, `DD MMM YY`, `D MMM YYYY`), with mixed use of zero-padding and day suffixes.
- There's a total of about 10 different date formats to be generated once finalized

**Merchant Helpers**
- `BASE_MERCHANTS`  
  Dictionary mapping canonical merchant “families” (e.g., `UBER`, `AMAZON`, `STARBUCKS`) to multiple real-world-style name variants. This is the source of truth for merchant categories.
  The first 16 key-value pairs have all values mapping to it's target company while the last 3 map to a category (restaruants, retail, service)
- `random_case_variant(s: str) -> str`  
  Randomly transforms the casing of a merchant string (upper, lower, title, or mixed case) to simulate inconsistent capitalization. Mixed case has the lowest chance of happening
- `maybe_add_spaces(s: str) -> str`  
  Occasionally adds extra leading, trailing, or internal spaces to simulate sloppy spacing with a chance
- `maybe_add_prefix_suffix(s: str) -> str`  
  Randomly prepends or appends tokens like `PAYPAL*`, `SQ*`, `ACH`, `.COM`, `INC`, `(ONLINE)` to simulate statement-style noise with a chance
- `maybe_add_typos(s: str) -> str`  
  WIntroduces a typo via character deletion or replacement in sufficiently long strings with a chance
- `maybe_add_regex_noise(s: str) -> str`  
  Injects special character sequences or tags (e.g., `.*`, `[TRIP]`, `(EATS)`, `.*UBR`) at the beginning or end of the merchant string with a chance
- `random_merchant() -> str`  
  Puts all the helpers together(random case and maybes): picks a base merchant from `BASE_MERCHANTS`, then applies casing noise, typos, prefixes/suffixes, regex-like noise, and spacing tweaks to produce a messy merchant field.

**Price Helpers**
- `format_amount_mixed() -> str`  
  Generates a randomized transaction amount between 1 and 2500 (with occasional negative refunds). It randomizes:
  - Whole vs decimal amounts  
  - Comma vs no comma  
  - Currency style (`plain`, `$`, `USD` before/after)  
  - Leading/trailing spaces  
  This simulates real financial statement amount formatting.

#### Main Methods

**Core Generator**
- `main(num_rows: int = 1000)`  
  Opens the output CSV file (`../datasets/synthetic_transactions.csv`), writes the header (`date, merchant, amount`), and then, for each row:
  - Samples a random date and formats it with `format_date_mixed`
  - Generates a noisy merchant string via `random_merchant`
  - Generates a noisy amount via `format_amount_mixed`  
  Finally, it writes all rows and prints a summary message with the number of generated rows.

**Interactive Wrapper (the one used in the demo**
- `creation_demo() -> bool`  
  CLI-style wrapper that:
  - Prompts the user for the desired number of rows  
  - Validates that the input is a positive integer  
  - Calls `main(num_rows)` on valid input  
  - Returns `True` on success, `False` on invalid input or error  
  This is the entry point used by the overall `pipeline.py` to run the creation step interactively.


### Data Cleaning

The most code and algorithm-heavy portion of this project, this data cleaning module reads the raw synthetic CSV, normalizes dates, merchants, and amounts, and writes a cleaned CSV plus basic error statistics. 

#### Date Helpers

- `DATE_PATTERNS`  
  A list of accepted datetime formats such as `YYYY-MM-DD`, `MM/DD/YYYY`, `MMM DD YYYY`, `DD-MM-YY`, `DD MMM YY`, and `DD MMM YYYY`. These cover all non-suffix date formats produced by the generator, except for `MMM Dth YY`, which is covered next

- `_suffix_date_regex`  
  A compiled regex that matches dates of the form `MMM Dth YY`, handling:
  - Three-letter month (mixed case allowed)  
  - One or two-digit day  
  - Required suffix (`st`, `nd`, `rd`, `th`)  
  - Two-digit year  

- `parse_date(raw: str) -> Optional[str]`  
  Normalizes any supported raw date string to ISO `YYYY-MM-DD`:
  - Strips whitespace  
  - Tries each format in `DATE_PATTERNS` via `datetime.strptime`  
  - If it is the `MMM Dth YY`, format, uses `_suffix_date_regex`
  - Returns ISO string on success, `None` on failure  

#### Merchant Helpers

- `BASE_MERCHANTS`  
  The mapping from canonical merchant families and specific restaurant/retail/service merchants to the various noisy names they may appear as in the raw data. This mirrors the creation module’s merchant universe and defines the target canonical space (27 final unique merchants). Instead of mapping to a category like int he creation, the service, retail, and restaruant categories are maped to their name.

- `_canonical_string(s: str) -> str`  
  Prepares strings for matching by:
  - Converting to uppercase  
  - Removing all non-alphanumeric characters  
  This collapses different punctuation, spacing, and symbol variants into a consistent canonical form.

- `BRAND_KEYS`  
  The set of 16 “brand-level” merchant families (e.g., `UBER`, `AMAZON`, `STARBUCKS`) that should be cleaned to their uppercase family name, rather than a specific restaurant or store name.

- `CANONICAL_BASES`  
  A precomputed list of `(canonical_base, canonical_output)` pairs built from `BASE_MERCHANTS`:
  - For brands in `BRAND_KEYS`, `canonical_output` is the brand key (e.g., `UBER`, `AMAZON`)  
  - For restaurant/retail/service entries, `canonical_output` is the original name (e.g., `Olive Garden`)  
  This serves as the lookup space for merchant normalization. This creates a key-value list of target values for the messy data to be mapped to

- The matching is done in two filters: one matches for strings after its canonicalized if there are no spelling errors, while the second filter uses levenshtein to map the strings with spelling errors by using edit-distance

- `levenshtein(a: str, b: str) -> int`  
  A standard Levenshtein edit-distance implementation:
  - Computes the minimum number of insertions, deletions, or substitutions to transform `a` into `b`  
  - Used to handle minor spelling errors in merchant strings.

- `clean_merchant(raw: str) -> str`  
  Cleans a raw merchant string and returns a canonical name:
  - Strips and validates the input  
  - Canonicalizes via `_canonical_string`  
  - **First pass:** finds the best match where a canonical base is contained within the canonical input (handles extra symbols/noise, chooses the longest match)  
  - **Second pass:** if no containment match, uses `levenshtein` distance across all bases and picks the output with the minimal edit distance  
  - Returns the canonical merchant (brand key or specific name) or `"ERROR"` if nothing reasonable can be mapped.

#### Amount Helpers

- Simplest to clean

- `parse_amount(raw: str) -> Optional[str]`  
  Normalizes messy amount strings to a standard two-decimal string:
  - Strips leading/trailing spaces  
  - Removes any `USD` (case-insensitive), `$` signs, and commas  
  - Converts to `float` and formats as `"{:.2f}"`  
  - Returns `None` if the cleaned string is empty  

#### Core Cleaning Logic

- `clean_csv() -> Dict[str, object]`  
  The main transformation function that:
  - Reads `INPUT_FILE` as a CSV using `csv.DictReader`  
  - For each row:
    - Extracts `date`, `merchant`, and `amount`  
    - Cleans them via `parse_date`, `clean_merchant`, and `parse_amount`  
    - Skips rows with invalid dates or amounts (incrementing `date_errors` / `amount_errors`)  
    - Counts unmapped merchants (where `clean_merchant` returns `"ERROR"`)  
    - Appends valid cleaned rows to `cleaned_rows`  
  - Writes the cleaned dataset to `OUTPUT_FILE` using `csv.DictWriter` with fields `["date", "merchant", "amount"]`  
  - Returns a summary dictionary containing:
    - `cleaned_rows` (list of cleaned row dicts)  
    - `total_rows`  
    - `date_errors`  
    - `amount_errors`  
    - `merchant_unmapped`  

#### Main Methods

- `main()` 
  Runs `clean_csv()` directly and prints:
  - Total raw rows and rows kept  
  - Counts of date parse errors, amount parse errors, and unmapped merchants  
  - The sorted list of unique cleaned merchant names  

- `cleaning_demo() -> bool` (used for the demo pipeline)
  Interactive wrapper used by the pipeline:
  - Shows input and output file paths  
  - Prompts the user with `Proceed with cleaning? (y/n)`  
  - On `"y"`:
    - Calls `clean_csv()`  
    - Prints the same summary stats as `main()`  
    - Prints a completion message and returns `True`  
  - On any other input:
    - Prints a cancel message and returns `False`  

### Data Analysis

The data analysis module is used to inspect the cleaned dataset and verify that the pipeline produced a structurally valid output. It also contains a personal exploratory analysis workflow used only for development and validation.

#### Exploratory Data Analysis (Development Only)

The notebook-based EDA is used for:
- Inspecting transaction amount distributions  
- Verifying date normalization consistency
- Generate basic visuals for self-exploration

This EDA is for personal exploration only and does **not** affect the pipeline demo or modify any datasets.

#### Core Analysis Logic

- `analysis_demo()`  
  The main pipeline-facing analysis function that:
  - Loads the cleaned CSV file  
  - Prints basic dataset diagnostics (shape and column names)  
  - Confirms that the cleaning stage produced a valid, structured dataset  

This serves as a lightweight verification step before downstream analytics or modeling.

#### Execution Behavior

- When run directly, the module executes `analysis_demo()` for standalone inspection  
- When imported by `pipeline.py`, only function definitions are loaded and execution is controlled entirely by the pipeline  

### Pipeline Controller

The pipeline module orchestrates the full workflow: data creation → data cleaning → data analysis, and allows the user to rerun the process in a single session.

- `main()`  
  - Runs creation, cleaning, and analysis in order  
  - Exits early if creation or cleaning is canceled  
  - Adds a short delay for 3 seconds before analysis for readability  
  - Prompts the user to rerun the full pipeline  

- Execution is controlled by:
  - `if __name__ == "__main__": main()`  
  - Ensures the loop only runs when executed directly

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
  
  Datasets/  
    synthetic_transactions.csv – Raw generated dataset  
    synthetic_transactions_clean.csv – Cleaned output dataset  

  Screenshots/
    2 Screenshots of my demo
   
  README.md – Project documentation  

## Creative Thinking Process + Challenges

With a more data science/analysis background, this option seemed like the best way for me to show my skills in data handling while working on and learning SWE principles and creating a clean project that can be cloned and used. My biggest tool was ChatGPT, as it helped me create templates for my code and READme, as well as provide suggestions for what to do. I had originally planned to import data, import fancy libraries to handle and clean the dataset, and then do extenside EDA on it becuase that's what I've done in the past on my Data Analysis projects. However, I needed to practice on what I knew about algorithms and create a parallel cleaning/creating process for this project to get myself outside my comfort zone. AI suggested me to use edit distance which I had just learned in my algorithms class to catch spelling errors, which was a part I spent a lot of time thinking about. The creation wasn't super hard to do, but the cleaning was difficult because I had to account for the first 16 merchants mapping to the name while the last 3 mapped to a category. ChatGPT helped me with suggestions on how to handle my cleaning process and eventually my pipeline, but in the end, I had to be the one to debug my code. Another challenge I had was that I was working on this project in Jupyter Notebook, and importing my three main files needed to by .py files and not .ipynb files. I worked through the terminal to convert my files every time I made edits. The pipeline had additional problems due to it running extra code from the three files that wasnt in the demo function. I spent a lot of time understanding the logic of the main fucntion and how to work with updating my code accordingly. In the end, I think I learned a lot, but still have much more to work on in the organization and robust-ness of my code.

## Future Improvements
- Use NLP (natural language processing) so that I'm not limited to a dictionary of merchants to generate and clean, can also be used to fix heavier typos
- Have funcitonality in my CLI to navigate through the messy and clean datasets (show row x to row y)
- Have multiple types of currencies and normalize it to one type
- Have Visual EDA in the CLI with bar graphs (I tried this but wasn't successful)
- Track performance metrics (how long it took to clean/create dataset)
- Have a configuration file instead of hard-coding it as a global varaible
- Implement SWE principles (Database to store all datasets, nice front end instead of CLI)


## Author
Benjamin Tran  
Computer Science
