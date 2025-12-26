import streamlit as st
import requests
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv

load_dotenv() 

# Page Configuration
st.set_page_config(
    page_title="GroAI.01 Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("GroAI.01 - AI Signal Mapping Dashboard")
st.markdown("""
This dashboard simulates LLMA-compatible LLM outputs and visualizes AI-generated expected returns.
It sends signal prompts and feature vectors to the local GroAI API for analysis.
""")

import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# --- Sidebar Inputs ---
st.sidebar.header("AIHedge.finance - AI Signal Mapping Dashboard")
prompt = st.sidebar.text_input("Prompt", value="bullish momentum")

# Dynamic Feature Loading
feature_names_history = []
feature_names_model = []
defaults_loaded = False

try:
    # Attempt to fetch feature names from the running API
    response = requests.get(f"{API_URL}/ai/features", timeout=1.0)
    if response.status_code == 200:
        data = response.json()
        feature_names_history = data.get("history_features", [])
        feature_names_model = data.get("model_features", [])
        defaults_loaded = True
        st.sidebar.success(f"Connected to API. Loaded {len(feature_names_history)} features.")
    else:
        st.sidebar.warning(f"API unreachable (Status {response.status_code}). Using fallback defaults.")
except requests.exceptions.ConnectionError:
    st.sidebar.error("API connection failed. Is the API server running?")
    st.sidebar.info("Using fallback/demo feature set.")
except Exception as e:
    st.sidebar.error(f"Error fetching features: {e}")

# Fallback defaults if API not reachable
if not defaults_loaded or not feature_names_history:
    # Default 4 features as per original snippet
    feature_names_history = [f"Feature {i+1}" for i in range(4)]
    # Default common technicals
    feature_names_model = ["ema_10", "ema_50", "rsi", "macd"]
    
# 1. Feature Vector Section (Inputs for History Prediction)
st.sidebar.subheader(f"Feature Vector ({len(feature_names_history)} values)")
feature_values = []

# Use an expander if there are many features to avoid cluttering 
with st.sidebar.expander("History Features (Normalized)", expanded=True):
    for i, name in enumerate(feature_names_history):
        # Default to 0.5 (midpoint) or a gradient for demo
        default_val = 0.1 * (i + 1) if i < 10 else 0.5
        if default_val > 1.0: default_val = 1.0
        
        val = st.slider(f"{name}", 0.0, 1.0, default_val, key=f"hist_{i}")
        feature_values.append(val)

# 2. Technicals Section (Inputs for Model Prediction)
st.sidebar.subheader("Technicals (Model Inputs)")
technicals = {}

with st.sidebar.expander("Model Technicals", expanded=False):
    for i, name in enumerate(feature_names_model):
        # Use number_input for potentially non-normalized values
        val = st.number_input(f"{name}", value=0.0, step=0.01, key=f"tech_{i}")
        technicals[name] = val

# Payload construction
# Note: api.py expects 'feature_values' (list) and 'technicals' (dict)
payload = {
    "prompt": prompt,
    "feature_values": feature_values, 
    "technicals": technicals
}

# --- Analysis Action ---
if st.button("Analyze Signal"):
    with st.spinner("Processing Inference..."):
        try:
            # Send request to API
            # Note: '/ai/signal_analysis' is the endpoint from api.py
            response = requests.post(f"{API_URL}/ai/signal_analysis", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                st.success("✓ Inference Complete")
                
                # --- Display Results ---
                col1, col2 = st.columns(2)
                
                # Column 1: LLM Output
                with col1:
                    st.subheader("LLM Output")
                    llm_out = result.get("llm_output", {})
                    st.json(llm_out)
                    
                    if isinstance(llm_out, dict):
                        comment = llm_out.get("comment", "")
                        if comment:
                             st.markdown(f"**Comment:** {comment}")
                
                # Column 2: Quantitative Results
                with col2:
                    st.subheader("Expected Returns")
                    
                    # Extract values
                    ret_history = result.get("expected_return_from_history", 0.0)
                    ret_model = result.get("expected_return_from_model", 0.0)
                    
                    # Try to get LLM return if structured
                    ret_llm = 0.0
                    if isinstance(llm_out, dict):
                        ret_llm = float(llm_out.get("expected_return", 0.0))
                    
                    st.metric("LLM-Based (Simulated)", ret_llm)
                    st.metric("History-Based (Stat)", ret_history)
                    st.metric("Model-Based (ML)", ret_model)
                
                # --- Visualization ---
                st.subheader("Return Comparison")
                fig, ax = plt.subplots(figsize=(8, 4))
                
                sources = ["LLM", "History", "Model"]
                values = [ret_llm, ret_history, ret_model]
                colors = ["#4caf50", "#2196f3", "#ff9800"]
                
                bars = ax.bar(sources, values, color=colors)
                ax.set_title("Expected Return Comparison")
                ax.set_ylabel("Return Value")
                ax.axhline(0, color='gray', linewidth=0.8) # Zero line
                
                # Label values on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.annotate(f'{height:.4f}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 3),  # 3 points vertical offset
                                textcoords="offset points",
                                ha='center', va='bottom')

                st.pyplot(fig)
                
            else:
                st.error(f"Server Error ({response.status_code}):")
                st.json(response.json()) # Try to show detail
                
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to API. Is 'make start-api' running?")
        except Exception as e:
            st.error(f"An error occurred: {e}")
