import unittest
import pandas as pd
from io import StringIO

from code_new import (
    file_loader,
    clean_whitespace,
    na_checker,
    duplicate_checker,
    data_enrich,
)

class TestDataCleaning(unittest.TestCase):

    def setUp(self):
        # Sample CSV data as if it were loaded from a file
        self.sample_csv = StringIO("""books,book_checkout,book_returned
Lord of the rings the return of the kind,"01/01/2023","05/01/2023"
Harry Potter,"10/02/2023","15/02/2023"
,, 
""")
        self.df = pd.read_csv(self.sample_csv)
    
    def test_clean_whitespace(self):
        cleaned = clean_whitespace(self.df.copy())
        self.assertTrue(cleaned.columns.equals(self.df.columns))  # Columns stay the same
        self.assertTrue(all(isinstance(val, str) or pd.isna(val)
                            for val in cleaned.iloc[:, 0]))  # Ensure first column is clean strings
    
    def test_na_checker_output(self):
        # Should return same DataFrame and print NA counts
        result = na_checker(self.df.copy(), label="Test Data")
        self.assertIsInstance(result, pd.DataFrame)

    def test_duplicate_checker_removes_duplicates(self):
        df = pd.DataFrame({
            'a': [1, 1, 2],
            'b': ['x', 'x', 'y']
        })
        cleaned = duplicate_checker(df, subset=['a', 'b'], label="Test")
        self.assertEqual(len(cleaned), 2)

    def test_data_enrich_books_typo_correction_and_drop(self):
        enriched = data_enrich(self.df.copy(), dataset_type="books")
        # Check typo corrected
        self.assertIn("Lord of the Rings: The Return of the King", enriched['books'].values)
        # Ensure rows with missing critical data are dropped
        self.assertFalse(enriched[['books', 'book_checkout', 'book_returned']].isnull().any().any())

    def test_data_enrich_customers_drops_blank_rows(self):
        df = pd.DataFrame({
            'name': ['John', None],
            'email': ['john@example.com', None]
        })
        enriched = data_enrich(df.copy(), dataset_type="customers")
        self.assertEqual(len(enriched), 1)

if __name__ == '__main__':
    unittest.main()