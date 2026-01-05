import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import Dict, List
import json


def format_currency(amount: float, currency: str = '₹') -> str:
    """Format amount as currency string."""
    return f"{currency}{amount:,.2f}"


def calculate_emi(principal: float, rate: float, tenure_months: int) -> float:
    """
    Calculate EMI for a loan.
    
    Args:
        principal: Loan amount
        rate: Annual interest rate (percentage)
        tenure_months: Loan tenure in months
        
    Returns:
        Monthly EMI amount
    """
    monthly_rate = rate / 12 / 100
    if monthly_rate == 0:
        return principal / tenure_months
    
    emi = principal * monthly_rate * (1 + monthly_rate) ** tenure_months / (
        (1 + monthly_rate) ** tenure_months - 1
    )
    return emi


def calculate_compound_interest(principal: float, rate: float, 
                               years: int, frequency: int = 12) -> float:
    """
    Calculate compound interest.
    
    Args:
        principal: Initial amount
        rate: Annual interest rate (percentage)
        years: Investment period in years
        frequency: Compounding frequency per year
        
    Returns:
        Final amount after compound interest
    """
    r = rate / 100
    n = frequency
    t = years
    
    amount = principal * (1 + r/n) ** (n*t)
    return amount


def calculate_future_value_sip(monthly_investment: float, rate: float, 
                               years: int) -> float:
    """
    Calculate future value of SIP (Systematic Investment Plan).
    
    Args:
        monthly_investment: Monthly investment amount
        rate: Annual expected return (percentage)
        years: Investment period in years
        
    Returns:
        Future value of SIP
    """
    monthly_rate = rate / 12 / 100
    months = years * 12
    
    if monthly_rate == 0:
        return monthly_investment * months
    
    fv = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    return fv


def plot_expense_breakdown(categories: Dict[str, float], 
                          title: str = "Expense Breakdown") -> plt.Figure:
    """
    Create a pie chart of expenses by category.
    
    Args:
        categories: Dictionary of category amounts
        title: Chart title
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Sort by amount
    sorted_categories = dict(sorted(categories.items(), 
                                   key=lambda x: x[1], 
                                   reverse=True))
    
    labels = list(sorted_categories.keys())
    sizes = list(sorted_categories.values())
    
    # Create color palette
    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                       startangle=90, colors=colors)
    
    # Beautify
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    return fig


def plot_trend(data: pd.Series, title: str, ylabel: str) -> plt.Figure:
    """
    Create a line plot showing trends over time.
    
    Args:
        data: Time series data
        title: Chart title
        ylabel: Y-axis label
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(data.index.astype(str), data.values, marker='o', 
            linewidth=2, markersize=8, color='#2E86AB')
    
    ax.fill_between(range(len(data)), data.values, alpha=0.3, color='#2E86AB')
    
    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    return fig


def create_interactive_dashboard(profile: Dict, 
                                 monthly_data: pd.DataFrame) -> go.Figure:
    """
    Create an interactive dashboard using Plotly.
    
    Args:
        profile: Financial profile
        monthly_data: Monthly transaction data
        
    Returns:
        Plotly figure
    """
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Monthly Income vs Expenses', 
                       'Expense Breakdown',
                       'Savings Trend', 
                       'Category Trends'),
        specs=[[{'type': 'bar'}, {'type': 'pie'}],
               [{'type': 'scatter'}, {'type': 'bar'}]]
    )
    
    # Income vs Expenses
    months = monthly_data.index.astype(str)
    fig.add_trace(
        go.Bar(name='Income', x=months, y=monthly_data['income']),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(name='Expenses', x=months, y=monthly_data['expenses']),
        row=1, col=1
    )
    
    # Expense breakdown
    categories = profile.get('expense_categories', {})
    fig.add_trace(
        go.Pie(labels=list(categories.keys()), 
               values=list(categories.values())),
        row=1, col=2
    )
    
    # Savings trend
    savings = monthly_data['income'] - monthly_data['expenses']
    fig.add_trace(
        go.Scatter(x=months, y=savings, mode='lines+markers', 
                  name='Savings', line=dict(color='green', width=3)),
        row=2, col=1
    )
    
    fig.update_layout(height=800, showlegend=True, 
                     title_text="Financial Dashboard")
    
    return fig


def export_to_excel(data: Dict[str, pd.DataFrame], 
                   filename: str = 'financial_report.xlsx'):
    """
    Export multiple dataframes to Excel with different sheets.
    
    Args:
        data: Dictionary of sheet_name: dataframe
        filename: Output filename
    """
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=True)
    
    print(f"Report exported to {filename}")


def generate_summary_stats(df: pd.DataFrame) -> Dict:
    """
    Generate summary statistics from transaction data.
    
    Args:
        df: Transaction DataFrame
        
    Returns:
        Dictionary of summary statistics
    """
    stats = {}
    
    # Overall stats
    stats['total_transactions'] = len(df)
    stats['date_range'] = (df['date'].min(), df['date'].max())
    
    # Income stats
    income = df[df['type'] == 'credit']
    stats['total_income'] = income['amount'].sum()
    stats['avg_income_transaction'] = income['amount'].mean()
    stats['income_sources'] = income['category'].nunique()
    
    # Expense stats
    expenses = df[df['type'] == 'debit']
    stats['total_expenses'] = abs(expenses['amount'].sum())
    stats['avg_expense_transaction'] = abs(expenses['amount'].mean())
    stats['expense_categories'] = expenses['category'].nunique()
    
    # Net
    stats['net_cashflow'] = stats['total_income'] - stats['total_expenses']
    
    return stats


def validate_input(value, value_type: str, min_val=None, max_val=None):
    """
    Validate user input.
    
    Args:
        value: Input value
        value_type: Expected type ('float', 'int', 'positive', etc.)
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Validated value
        
    Raises:
        ValueError: If validation fails
    """
    if value_type == 'float':
        try:
            value = float(value)
        except ValueError:
            raise ValueError(f"Invalid float value: {value}")
    
    elif value_type == 'int':
        try:
            value = int(value)
        except ValueError:
            raise ValueError(f"Invalid integer value: {value}")
    
    elif value_type == 'positive':
        value = float(value)
        if value <= 0:
            raise ValueError(f"Value must be positive: {value}")
    
    if min_val is not None and value < min_val:
        raise ValueError(f"Value {value} is below minimum {min_val}")
    
    if max_val is not None and value > max_val:
        raise ValueError(f"Value {value} exceeds maximum {max_val}")
    
    return value


def load_config(config_path: str = 'config.yaml') -> Dict:
    """Load configuration from YAML file."""
    import yaml
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"Config file not found: {config_path}")
        return {}


def save_json(data: Dict, filepath: str):
    """Save dictionary as JSON file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    print(f"Data saved to {filepath}")


def load_json(filepath: str) -> Dict:
    """Load JSON file as dictionary."""
    with open(filepath, 'r') as f:
        return json.load(f)


def create_budget_comparison_chart(current: Dict, optimized: Dict) -> plt.Figure:
    """
    Create side-by-side comparison of current vs optimized budget.
    
    Args:
        current: Current budget by category
        optimized: Optimized budget by category
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    categories = list(set(current.keys()) | set(optimized.keys()))
    x = np.arange(len(categories))
    width = 0.35
    
    current_values = [current.get(cat, 0) for cat in categories]
    optimized_values = [optimized.get(cat, 0) for cat in categories]
    
    bars1 = ax.bar(x - width/2, current_values, width, label='Current', 
                   color='#E63946')
    bars2 = ax.bar(x + width/2, optimized_values, width, label='Optimized', 
                   color='#06FFA5')
    
    ax.set_xlabel('Category', fontsize=12, fontweight='bold')
    ax.set_ylabel('Amount (₹)', fontsize=12, fontweight='bold')
    ax.set_title('Budget Comparison: Current vs Optimized', 
                fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig


class ProgressTracker:
    """Track progress toward financial goals."""
    
    def __init__(self, goal_name: str, target: float, current: float = 0):
        self.goal_name = goal_name
        self.target = target
        self.current = current
        self.history = []
    
    def update(self, amount: float, date: str = None):
        """Update progress."""
        self.current += amount
        self.history.append({
            'date': date or pd.Timestamp.now().strftime('%Y-%m-%d'),
            'amount': amount,
            'total': self.current
        })
    
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        return (self.current / self.target * 100) if self.target > 0 else 0
    
    def remaining(self) -> float:
        """Calculate remaining amount."""
        return max(0, self.target - self.current)
    
    def plot_progress(self) -> plt.Figure:
        """Plot progress over time."""
        if not self.history:
            return None
        
        df = pd.DataFrame(self.history)
        df['date'] = pd.to_datetime(df['date'])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(df['date'], df['total'], marker='o', linewidth=2, 
               markersize=8, label='Progress')
        ax.axhline(y=self.target, color='r', linestyle='--', 
                  linewidth=2, label='Target')
        
        ax.fill_between(df['date'], df['total'], alpha=0.3)
        
        ax.set_title(f'Progress: {self.goal_name}', 
                    fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Amount (₹)', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
