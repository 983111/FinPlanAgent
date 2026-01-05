import pytest
import pandas as pd
from src.parser import TransactionParser


class TestTransactionParser:
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = TransactionParser()
        
    def test_parse_csv_basic(self, tmp_path):
        """Test basic CSV parsing."""
        # Create a temporary CSV file
        csv_content = """Date,Description,Amount,Type
2024-01-01,Salary,50000,credit
2024-01-02,Grocery,-2000,debit
2024-01-03,Rent,-15000,debit"""
        
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        df = self.parser.parse_csv(str(csv_file))
        
        assert len(df) == 3
        assert list(df.columns) == ['date', 'description', 'amount', 'type']
        assert df['amount'].sum() == 33000
        
    def test_clean_amount(self):
        """Test amount cleaning."""
        assert self.parser._clean_amount("₹1,000.50") == 1000.50
        assert self.parser._clean_amount("$2,500") == 2500.0
        assert self.parser._clean_amount("(500)") == -500.0
        assert self.parser._clean_amount(1234.56) == 1234.56
        
    def test_validate_data(self):
        """Test data validation."""
        df = pd.DataFrame({
            'date': pd.to_datetime(['2024-01-01', '2024-01-02']),
            'description': ['test1', 'test2'],
            'amount': [100, -50],
            'type': ['credit', 'debit']
        })
        
        validation = self.parser.validate_data(df)
        
        assert validation['valid'] == True
        assert validation['stats']['transaction_count'] == 2
        assert 'date_range' in validation['stats']
        
    def test_parse_manual(self):
        """Test manual transaction parsing."""
        transactions = [
            {'date': '2024-01-01', 'description': 'Salary', 'amount': 50000},
            {'date': '2024-01-02', 'description': 'Rent', 'amount': -15000}
        ]
        
        df = self.parser.parse_manual(transactions)
        
        assert len(df) == 2
        assert df['type'].tolist() == ['credit', 'debit']
        
    def test_invalid_csv(self):
        """Test handling of invalid CSV."""
        with pytest.raises(FileNotFoundError):
            self.parser.parse_csv('nonexistent.csv')
            
    def test_missing_columns(self):
        """Test handling of missing required columns."""
        transactions = [
            {'date': '2024-01-01', 'amount': 100}  # Missing description
        ]
        
        with pytest.raises(ValueError):
            self.parser.parse_manual(transactions)
