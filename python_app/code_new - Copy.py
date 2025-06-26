import pandas as pd

def file_loader(filepath):
    """Loads a CSV file and standardizes column names."""
    print(f"Loading file: {filepath}")
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

def clean_whitespace(df):
    """Strips whitespace from string cells."""
    return df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

def na_checker(df, label="Data"):
    """Reports and optionally handles missing values."""
    total_na = df.isna().sum().sum()
    print(f"{label}: Total missing values: {total_na}")
    print(df.isnull().sum())
    return df

def duplicate_checker(df, subset=None, label="Data"):
    """Checks for duplicate rows based on optional subset of columns."""
    dups = df.duplicated(subset=subset)
    print(f"{label}: Duplicate rows found: {dups.sum()}")
    return df[~dups]

def data_enrich(df, dataset_type):
    """Performs dataset-specific cleaning and enrichment."""
    if dataset_type == "books":
        # Remove quotes from date columns
        df['book_checkout'] = df['book_checkout'].astype(str).str.replace('"', '', regex=False)
        df['book_returned'] = df['book_returned'].astype(str).str.replace('"', '', regex=False)

        # Convert to datetime (correct format!)
        df['book_checkout'] = pd.to_datetime(df['book_checkout'], format='%d/%m/%Y', errors='coerce')
        df['book_returned'] = pd.to_datetime(df['book_returned'], format='%d/%m/%Y', errors='coerce')

        # Fix known typos
        df['books'] = df['books'].replace({
            'Lord of the rings the return of the kind': 'Lord of the Rings: The Return of the King'
        })

        # Preview rows that will be dropped
        missing = df[df[['books', 'book_checkout', 'book_returned']].isnull().any(axis=1)]
        if not missing.empty:
            print("Rows with missing critical fields (to be dropped):")
            print(missing)

        # Drop rows with missing critical data
        df = df.dropna(subset=['books', 'book_checkout', 'book_returned'])

    elif dataset_type == "customers":
        # Drop fully blank rows
        df = df.dropna(how='all')

    return df

def save_cleaned_data(df, output_path):
    """Saves DataFrame to a CSV file."""
    df.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}")

def main():
    # -------- Books Dataset --------
    books_file = r"03_Library Systembook.csv"
    books_output = r"cleaned_library_data.csv"
    books_df = file_loader(books_file)
    books_df = clean_whitespace(books_df)
    books_df = na_checker(books_df, "Books")
    books_df = duplicate_checker(books_df, label="Books")
    books_df = data_enrich(books_df, dataset_type="books")

    print("Final books data preview:")
    print(books_df.head())
    save_cleaned_data(books_df, books_output)

    # -------- Customers Dataset --------
    customers_file = r"03_Library SystemCustomers.csv"
    customers_output = r"cleaned_customers.csv"
    customers_df = file_loader(customers_file)
    customers_df = clean_whitespace(customers_df)
    customers_df = na_checker(customers_df, "Customers")
    customers_df = duplicate_checker(customers_df, label="Customers")
    customers_df = data_enrich(customers_df, dataset_type="customers")

    print("Final customers data preview:")
    print(customers_df.head())
    save_cleaned_data(customers_df, customers_output)

if __name__ == "__main__":
    main()

import pandas as pd
from sqlalchemy import create_engine

# Database connection settings
server = 'localhost'
database = 'LibrarySystem'
driver = 'ODBC Driver 17 for SQL Server'

# Create SQLAlchemy connection string
connection_string = (
    f"mssql+pyodbc://@{server}/{database}"
    f"?trusted_connection=yes&driver={driver}"
)

# Create engine
engine = create_engine(connection_string)

# Load cleaned CSVs
books = pd.read_csv(r'C:\Users\Admin\Desktop\QA_module_5\python_app\cleaned_library_data.csv')
customers = pd.read_csv(r'C:\Users\Admin\Desktop\QA_module_5\python_app\cleaned_customers.csv')

# Upload to SQL Server
books.to_sql(name='Books', con=engine, if_exists='replace', index=False)
customers.to_sql(name='Customers', con=engine, if_exists='replace', index=False)

print("Upload to SQL Server completed.")

if __name__ == "__main__":
    main()
