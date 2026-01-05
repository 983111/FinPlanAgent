import pandas as pd
import pdfplumber
from datetime import datetime
from typing import List, Dict, Optional
import re


class TransactionParser:
    """Parse financial transactions from various file formats."""
    
    def __init__(self):
        self.supported_formats = ['csv', 'pdf', 'xlsx']
        
    def parse_csv(self, filepath: str, 
                  date_col: str = 'Date',
                  desc_col: str = 'Description',
                  amount_col: str = 'Amount',
                  type_col: Optional[str] = None) -> pd.DataFrame:
        """
        Parse transactions from CSV file.
        
        Args:
            filepath: Path to CSV file
            date_col: Name of date column
            desc_col: Name of description column
            amount_col: Name of amount column
            type_col: Name of transaction type column (credit/debit)
            
        Returns:
            DataFrame with standardized columns
        """
        df = pd.read_csv(filepath)
        
        # Standardize column names
        column_mapping = {
            date_col: 'date',
            desc_col: 'description',
            amount_col: 'amount'
        }
        
        if type_col and type_col in df.columns:
            column_mapping[type_col] = 'type'
            
        df = df.rename(columns=column_mapping)
        
        # Parse dates
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Clean amounts
        df['amount'] = df['amount'].apply(self._clean_amount)
        
        # Infer transaction type if not provided
        if 'type' not in df.columns:
            df['type'] = df['amount'].apply(
                lambda x: 'credit' if x > 0 else 'debit'
            )
        
        # Clean descriptions
        df['description'] = df['description'].str.strip().str.lower()
        
        return df[['date', 'description', 'amount', 'type']].dropna()
    
    def parse_pdf(self, filepath: str) -> pd.DataFrame:
        """
        Extract transactions from bank statement PDF.
        
        Args:
            filepath: Path to PDF file
            
        Returns:
            DataFrame with parsed transactions
        """
        transactions = []
        
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    page_transactions = self._extract_transactions_from_text(text)
                    transactions.extend(page_transactions)
        
        if not transactions:
            raise ValueError("No transactions found in PDF")
            
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['amount'] = df['amount'].apply(self._clean_amount)
        
        return df[['date', 'description', 'amount', 'type']].dropna()
    
    def parse_manual(self, transactions: List[Dict]) -> pd.DataFrame:
        """
        Parse manually entered transactions.
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            DataFrame with standardized columns
        """
        df = pd.DataFrame(transactions)
        
        required_cols = {'date', 'description', 'amount'}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            raise ValueError(f"Missing required columns: {missing}")
        
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['amount'] = df['amount'].apply(self._clean_amount)
        
        if 'type' not in df.columns:
            df['type'] = df['amount'].apply(
                lambda x: 'credit' if x > 0 else 'debit'
            )
        
        return df[['date', 'description', 'amount', 'type']].dropna()
    
    def _clean_amount(self, amount) -> float:
        """Clean and convert amount to float."""
        if isinstance(amount, (int, float)):
            return float(amount)
        
        if isinstance(amount, str):
            # Remove currency symbols and commas
            cleaned = re.sub(r'[₹$,\s]', '', amount)
            # Handle negative signs
            if '(' in cleaned or cleaned.endswith('-'):
                cleaned = cleaned.replace('(', '').replace(')', '').replace('-', '')
                return -float(cleaned)
            return float(cleaned)
        
        return 0.0
    
    def _extract_transactions_from_text(self, text: str) -> List[Dict]:
        """
        Extract transaction data from PDF text using regex patterns.
        
        Args:
            text: Raw text from PDF page
            
        Returns:
            List of transaction dictionaries
        """
        transactions = []
        
        # Pattern: date, description, amount
        # Example: "01/12/2023  GROCERY STORE  -45.99"
        pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(.+?)\s+([-+]?\d+[,.]?\d*\.?\d*)'
        
        matches = re.finditer(pattern, text)
        for match in matches:
            date_str, desc, amount_str = match.groups()
            
            try:
                trans = {
                    'date': date_str,
                    'description': desc.strip().lower(),
                    'amount': self._clean_amount(amount_str),
                    'type': 'credit' if float(amount_str.replace(',', '')) > 0 else 'debit'
                }
                transactions.append(trans)
            except (ValueError, AttributeError):
                continue
        
        return transactions
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Validate parsed transaction data.
        
        Args:
            df: Transaction DataFrame
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        # Check for required columns
        required = {'date', 'description', 'amount', 'type'}
        missing = required - set(df.columns)
        if missing:
            validation['valid'] = False
            validation['errors'].append(f"Missing columns: {missing}")
            return validation
        
        # Check for null values
        null_counts = df.isnull().sum()
        if null_counts.any():
            validation['warnings'].append(f"Null values found: {null_counts[null_counts > 0].to_dict()}")
        
        # Check date range
        if not df.empty:
            date_range = (df['date'].min(), df['date'].max())
            validation['stats']['date_range'] = date_range
            validation['stats']['transaction_count'] = len(df)
            validation['stats']['total_credits'] = df[df['type'] == 'credit']['amount'].sum()
            validation['stats']['total_debits'] = abs(df[df['type'] == 'debit']['amount'].sum())
        
        # Check for duplicates
        duplicates = df.duplicated(subset=['date', 'description', 'amount']).sum()
        if duplicates > 0:
            validation['warnings'].append(f"Found {duplicates} potential duplicate transactions")
        
        return validation
