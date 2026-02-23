import streamlit as st
import os
import sys
import re
import pandas as pd
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.parser import TransactionParser
from src.analyzer import TransactionAnalyzer
from src.profile_builder import ProfileBuilder
from src.optimizer import BudgetOptimizer
from src.agent import FinancialAgent

load_dotenv()

st.set_page_config(page_title="FinPlan Agent Web Test", layout="wide")
st.title("🤖 FinPlan Agent - Web Interface")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_ready" not in st.session_state:
    st.session_state.agent_ready = False

with st.sidebar:
    st.header("Step 1: Setup")
    api_key = st.text_input("Enter your API Key:", type="password")
    
    # NEW: Let the user choose how the AI should handle the CSV
    analysis_mode = st.radio(
        "Choose Analysis Mode:",
        ["Budget Planner (Requires Date, Description, Amount)", "Generic CSV Analyzer (Any Data)"]
    )
    
    st.header("Step 2: Upload Data")
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    
    if st.button("Start Agent") and uploaded_file and api_key:
        with st.spinner("Processing data..."):
            os.environ["K2THINK_API_KEY"] = api_key
            
            with open("temp_data.csv", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                agent = FinancialAgent(api_key=api_key)
                
                if "Budget Planner" in analysis_mode:
                    # ORIGINAL LOGIC: Strict personal finance parsing
                    parser = TransactionParser()
                    df = parser.parse_csv("temp_data.csv")
                    
                    analyzer = TransactionAnalyzer()
                    df_cat = analyzer.categorize(df)
                    patterns = analyzer.compute_spending_patterns(df_cat)
                    
                    builder = ProfileBuilder()
                    profile = builder.build(df_cat, current_savings=50000)
                    
                    optimizer = BudgetOptimizer()
                    budget = optimizer.optimize(
                        income=profile.monthly_income,
                        current_spending=profile.expense_categories,
                        savings_goal_pct=20
                    )
                    
                    budget_data = budget.to_dict()
                    if 'constraints_met' in budget_data:
                        budget_data['constraints_met'] = {k: str(v) for k, v in budget_data['constraints_met'].items()}
                    
                    agent.initialize_context(
                        profile=profile.to_dict(),
                        transactions_summary=patterns,
                        budget_plan=budget_data
                    )
                
                else:
                    # NEW LOGIC: Generic CSV Analysis
                    # Read the CSV using pandas
                    df = pd.read_csv("temp_data.csv")
                    
                    # Limit to first 300 rows so we don't crash the AI context limit
                    if len(df) > 300:
                        st.warning(f"File is large ({len(df)} rows). Analyzing the first 300 rows to fit AI memory limits.")
                        df = df.head(300)
                    
                    # Convert dataframe to a string format the AI can read easily
                    csv_string = df.to_csv(index=False)
                    
                    # Initialize agent with the raw text
                    agent.initialize_generic_csv_context(csv_text=csv_string, filename=uploaded_file.name)

                st.session_state.agent = agent
                st.session_state.agent_ready = True
                
                # Clear chat history when starting a new agent
                st.session_state.messages = []
                st.success(f"✅ Agent initialized in {analysis_mode.split('(')[0].strip()} mode!")
                
            except Exception as e:
                st.error(f"Error initializing agent: {e}")

# 4. Main Chat Interface
if st.session_state.agent_ready:
    st.header("💬 Chat with your Financial Agent")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    if prompt := st.chat_input("Ask a question about your data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                raw_response = st.session_state.agent.chat(prompt)
                
                # Filter out the <think> tags for a clean response
                clean_response = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL).strip()
                
                st.markdown(clean_response)
                st.session_state.messages.append({"role": "assistant", "content": clean_response})
else:
    st.info("👈 Please enter your API key, select a mode, and upload your CSV file in the sidebar to start chatting.")
