#!/usr/bin/env python3
"""
FinPlanAgent - Quick Start Script

Usage:
    python main.py --file data/transactions.csv
    python main.py --demo
"""

import argparse
import os
from dotenv import load_dotenv

from src.parser import TransactionParser
from src.analyzer import TransactionAnalyzer
from src.profile_builder import ProfileBuilder
from src.optimizer import BudgetOptimizer
from src.agent import FinancialAgent
from src.simulator import WhatIfSimulator
from src.explainer import Explainer


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_analysis(filepath, current_savings=50000, use_agent=False):
    """Run complete financial analysis pipeline."""
    
    print_header("FINPLANAGENT - AI Financial Advisor")
    
    # Step 1: Parse transactions
    print("📄 Step 1: Parsing transactions...")
    parser = TransactionParser()
    df = parser.parse_csv(filepath)
    print(f"   ✓ Loaded {len(df)} transactions")
    
    validation = parser.validate_data(df)
    if validation['valid']:
        print("   ✓ Data validation passed")
    else:
        print("   ⚠ Validation warnings:")
        for warning in validation['warnings']:
            print(f"     - {warning}")
    
    # Step 2: Analyze transactions
    print("\n📊 Step 2: Analyzing spending patterns...")
    analyzer = TransactionAnalyzer()
    df_categorized = analyzer.categorize(df)
    patterns = analyzer.compute_spending_patterns(df_categorized)
    
    print(f"   ✓ Total Income: ₹{patterns['total_income']:,.2f}")
    print(f"   ✓ Total Expenses: ₹{patterns['total_expenses']:,.2f}")
    print(f"   ✓ Net Savings: ₹{patterns['net_savings']:,.2f}")
    
    # Step 3: Build profile
    print("\n👤 Step 3: Building financial profile...")
    builder = ProfileBuilder()
    profile = builder.build(df_categorized, current_savings=current_savings)
    
    print(f"   ✓ Monthly Income: ₹{profile.monthly_income:,.2f}")
    print(f"   ✓ Savings Rate: {profile.savings_rate:.1f}%")
    print(f"   ✓ Emergency Fund: {profile.emergency_fund_months:.1f} months")
    print(f"   ✓ Risk Tolerance: {profile.risk_tolerance.upper()}")
    
    # Step 4: Assess health
    print("\n💊 Step 4: Assessing financial health...")
    health = builder.assess_financial_health(profile)
    
    print(f"   ✓ Overall Score: {health['overall_score']:.1f}/100")
    print(f"   ✓ Rating: {health['health_rating']}")
    
    # Step 5: Optimize budget
    print("\n💰 Step 5: Optimizing budget...")
    optimizer = BudgetOptimizer()
    budget = optimizer.optimize(
        income=profile.monthly_income,
        current_spending=profile.expense_categories,
        savings_goal_pct=20
    )
    
    print(f"   ✓ Optimization Status: {budget.optimization_status}")
    print(f"   ✓ Expected Savings: ₹{budget.expected_savings:,.2f}/month")
    
    # Step 6: Generate insights
    print("\n💡 Step 6: Generating insights...")
    insights = analyzer.generate_insights(df_categorized)
    
    for insight in insights[:3]:
        print(f"   • {insight}")
    
    # Step 7: Simulate scenarios
    print("\n🎯 Step 7: Running what-if scenarios...")
    simulator = WhatIfSimulator(profile.to_dict())
    
    # Example: Car purchase simulation
    car_scenario = simulator.simulate_purchase(
        item="Car",
        amount=500000,
        payment_plan="loan",
        duration_months=60,
        interest_rate=8.5
    )
    
    print(f"   • Car Purchase Scenario:")
    print(f"     Feasibility: {car_scenario.feasibility_score:.0f}/100")
    if car_scenario.recommendations:
        print(f"     {car_scenario.recommendations[0]}")
    
    # Step 8: AI Agent (optional)
    if use_agent:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print("\n🤖 Step 8: Initializing AI Agent...")
            agent = FinancialAgent(api_key=api_key)
            agent.initialize_context(
                profile=profile.to_dict(),
                transactions_summary=patterns,
                budget_plan=budget.to_dict()
            )
            print("   ✓ AI Agent ready for questions")
            
            # Example query
            response = agent.chat("What should I focus on to improve my finances?")
            print(f"\n   Agent Response:\n   {response[:200]}...")
        else:
            print("\n⚠ OpenAI API key not found. Skipping AI agent step.")
    
    # Generate report
    print("\n📝 Generating comprehensive report...")
    explainer = Explainer()
    report = explainer.generate_report(
        profile=profile.to_dict(),
        analysis=patterns,
        recommendations=health['recommendations']
    )
    
    # Save report
    os.makedirs('reports', exist_ok=True)
    report_path = 'reports/financial_analysis.txt'
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"   ✓ Report saved to {report_path}")
    
    # Summary
    print_header("ANALYSIS COMPLETE")
    print("Key Takeaways:")
    print(f"  • Current savings rate: {profile.savings_rate:.1f}%")
    print(f"  • Potential monthly savings with optimization: ₹{budget.expected_savings:,.2f}")
    print(f"  • Financial health: {health['health_rating']}")
    print(f"\nFull report available at: {report_path}")
    print("\nNext steps:")
    for i, rec in enumerate(health['recommendations'][:3], 1):
        print(f"  {i}. {rec}")


def run_demo():
    """Run demo with sample data."""
    print("\n🎬 Running demo with sample data...\n")
    run_analysis('data/sample_transactions.csv', current_savings=50000)


def interactive_mode():
    """Run interactive mode."""
    print_header("INTERACTIVE MODE")
    
    print("Let's set up your financial analysis!")
    print()
    
    # Get file path
    filepath = input("Path to your transactions CSV file (or press Enter for demo): ").strip()
    if not filepath:
        filepath = 'data/sample_transactions.csv'
        print(f"Using demo file: {filepath}")
    
    # Get current savings
    try:
        savings_input = input("\nYour current savings (press Enter for ₹50,000): ").strip()
        current_savings = float(savings_input) if savings_input else 50000
    except ValueError:
        print("Invalid input, using default ₹50,000")
        current_savings = 50000
    
    # Ask about AI agent
    use_agent_input = input("\nUse AI agent for personalized advice? (y/n, default: n): ").strip().lower()
    use_agent = use_agent_input == 'y'
    
    if use_agent and not os.getenv('OPENAI_API_KEY'):
        print("\n⚠ Warning: No OpenAI API key found in .env file")
        print("AI agent will be skipped. Set OPENAI_API_KEY to use this feature.")
        use_agent = False
    
    print()
    run_analysis(filepath, current_savings, use_agent)


def main():
    """Main entry point."""
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description='FinPlanAgent - AI-Driven Personal Financial Advisor'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Path to transactions CSV file'
    )
    parser.add_argument(
        '--savings',
        type=float,
        default=50000,
        help='Current savings amount (default: 50000)'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demo with sample data'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--use-agent',
        action='store_true',
        help='Enable AI agent (requires OpenAI API key)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.demo:
            run_demo()
        elif args.interactive:
            interactive_mode()
        elif args.file:
            run_analysis(args.file, args.savings, args.use_agent)
        else:
            # No arguments provided, show help
            print_header("FINPLANAGENT")
            print("AI-Driven Personal Financial Advisor\n")
            print("Usage examples:")
            print("  python main.py --demo                    # Run with sample data")
            print("  python main.py --interactive             # Interactive mode")
            print("  python main.py --file data/my_data.csv   # Analyze your data")
            print("  python main.py --help                    # Show all options")
            print("\nFor detailed documentation, see README.md and GETTING_STARTED.md")
    
    except FileNotFoundError as e:
        print(f"\n❌ Error: File not found - {e}")
        print("Please check the file path and try again.")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check the error message and try again.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
