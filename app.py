import streamlit as st
import os
import sys
import re
from dotenv import load_dotenv

# FIX 1: This ensures Streamlit Cloud can find your 'src' folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the core modules from your existing source code
from src.parser import TransactionParser
from src.analyzer import TransactionAnalyzer
from src.profile_builder import ProfileBuilder
from src.optimizer import BudgetOptimizer
from src.agent import FinancialAgent

# Load environment variables
load_dotenv()

# 1. Setup the Webpage Layout
st.set_page_config(page_title="FinPlan Agent Web Test", layout="wide")
st.title("🤖 FinPlan Agent - Web Interface")

# Initialize "session state" to remember the chat history and if the agent is ready
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_ready" not in st.session_state:
    st.session_state.agent_ready = False

# 2. Sidebar for Setup (API Key and File Upload)
with st.sidebar:
    st.header("Step 1: Setup")
    api_key = st.text_input("Enter your API Key:", type="password")
    
    st.header("Step 2: Upload Data")
    uploaded_file = st.file_uploader("Upload transactions CSV", type=['csv'])
    
    # 3. Initialize the Agent when the button is clicked
    if st.button("Start Agent") and uploaded_file and api_key:
        with st.spinner("Processing data..."):
            # Set the API key based on your agent.py requirements
            os.environ["K2THINK_API_KEY"] = api_key
            
            # Save the uploaded file temporarily so the parser can read it
            with open("temp_data.csv", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                # Step A: Parse transactions
                parser = TransactionParser()
                df = parser.parse_csv("temp_data.csv")
                
                # Step B: Analyze
                analyzer = TransactionAnalyzer()
                df_cat = analyzer.categorize(df)
                patterns = analyzer.compute_spending_patterns(df_cat)
                
                # Step C: Build profile (assuming a default current savings of 50,000)
                builder = ProfileBuilder()
                profile = builder.build(df_cat, current_savings=50000)
                
                # Step D: Optimize budget
                optimizer = BudgetOptimizer()
                budget = optimizer.optimize(
                    income=profile.monthly_income,
                    current_spending=profile.expense_categories,
                    savings_goal_pct=20
                )
                
                # Step E: Initialize the AI Agent
                agent = FinancialAgent(api_key=api_key)
                
                # FIX 2: Convert Booleans to strings so they are JSON serializable
                budget_data = budget.to_dict()
                if 'constraints_met' in budget_data:
                    budget_data['constraints_met'] = {k: str(v) for k, v in budget_data['constraints_met'].items()}
                
                agent.initialize_context(
                    profile=profile.to_dict(),
                    transactions_summary=patterns,
                    budget_plan=budget_data  # Use the cleaned data here
                )
                
                # Save the agent into the session state so we can chat with it
                st.session_state.agent = agent
                st.session_state.agent_ready = True
                st.success("✅ Agent initialized successfully!")
                
            except Exception as e:
                st.error(f"Error initializing agent: {e}")

# 4. Main Chat Interface
if st.session_state.agent_ready:
    st.header("💬 Chat with your Financial Agent")
    
    # Display previous chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # Input box for new user messages
    if prompt := st.chat_input("Ask a question about your finances..."):
        # Add the user's message to the screen
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Send the message to the AI and print the response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.agent.chat(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
else:
    st.info("👈 Please enter your API key and upload your CSV file in the sidebar to start chatting.")
