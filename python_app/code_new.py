import pandas as pd
from sqlalchemy import create_engine
import os

# ---------- Functions ----------

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
    """Checks for duplicate rows."""
    dups = df.duplicated(subset=subset)
    print(f"{label}: Duplicate rows found: {dups.sum()}")
    return df[~dups]

def data_enrich(df, dataset_type):
    """Cleans and enriches data for books/customers."""
    if dataset_type == "books":
        df['book_checkout'] = df['book_checkout'].astype(str).str.replace('"', '', regex=False)
        df['book_returned'] = df['book_returned'].astype(str).str.replace('"', '', regex=False)

        df['book_checkout'] = pd.to_datetime(df['book_checkout'], format='%d/%m/%Y', errors='coerce')
        df['book_returned'] = pd.to_datetime(df['book_returned'], format='%d/%m/%Y', errors='coerce')

        df['books'] = df['books'].replace({
            'Lord of the rings the return of the kind': 'Lord of the Rings: The Return of the King'
        })

        missing = df[df[['books', 'book_checkout', 'book_returned']].isnull().any(axis=1)]
        if not missing.empty:
            print("Rows with missing critical fields (to be dropped):")
            print(missing)

        df = df.dropna(subset=['books', 'book_checkout', 'book_returned'])

    elif dataset_type == "customers":
        df = df.dropna(how='all')

    return df

def save_cleaned_data(df, output_path):
    """Saves DataFrame to a CSV file."""
    df.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}")

# ---------- Metric Tracker ----------
metrics = []

def log_metric(dataset, metric, value):
    metrics.append({"Dataset": dataset, "Metric": metric, "Value": value})


# ---------- Main Script ----------

def main():
    # File paths
    books_file = "03_Library Systembook.csv"
    customers_file = "03_Library SystemCustomers.csv"
    books_output = "cleaned_library_data.csv"
    customers_output = "cleaned_customers.csv"
    metrics_output = "data_quality_report.csv"

    # Books
    books_df = file_loader(books_file)
    log_metric("Books", "Initial Rows", len(books_df))
    log_metric("Books", "Missing Values (Before)", books_df.isna().sum().sum())
    log_metric("Books", "Duplicates Removed", books_df.duplicated().sum())

    books_df = clean_whitespace(books_df)
    books_df = na_checker(books_df, "Books")
    books_df = duplicate_checker(books_df, label="Books")

    before_drop = len(books_df)
    books_df = data_enrich(books_df, dataset_type="books")
    log_metric("Books", "Rows Dropped (NaNs)", before_drop - len(books_df))

    save_cleaned_data(books_df, books_output)

    # Customers
    customers_df = file_loader(customers_file)
    log_metric("Customers", "Initial Rows", len(customers_df))
    log_metric("Customers", "Missing Values (Before)", customers_df.isna().sum().sum())
    log_metric("Customers", "Duplicates Removed", customers_df.duplicated().sum())

    customers_df = clean_whitespace(customers_df)
    customers_df = na_checker(customers_df, "Customers")
    customers_df = duplicate_checker(customers_df, label="Customers")

    before_drop = len(customers_df)
    customers_df = data_enrich(customers_df, dataset_type="customers")
    log_metric("Customers", "Rows Dropped (NaNs)", before_drop - len(customers_df))

    save_cleaned_data(customers_df, customers_output)

    # Save metrics
    metrics_df = pd.DataFrame(metrics)
    save_cleaned_data(metrics_df, metrics_output)

    # Upload to SQL
    upload_to_sql(books_df, customers_df, metrics_df)

def upload_to_sql(books, customers, metrics):
    server = 'localhost'
    database = 'LibrarySystem'
    driver = 'ODBC Driver 17 for SQL Server'
    connection_string = (
        f"mssql+pyodbc://@{server}/{database}"
        f"?trusted_connection=yes&driver={driver}"
    )
    engine = create_engine(connection_string)

    books.to_sql(name='Books', con=engine, if_exists='replace', index=False)
    customers.to_sql(name='Customers', con=engine, if_exists='replace', index=False)
    metrics.to_sql(name='DataQuality', con=engine, if_exists='replace', index=False)
    print("Upload to SQL Server completed.")

# ---------- Entry ----------
if __name__ == "__main__":
    main()

