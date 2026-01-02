import streamlit as st
import requests
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv() 

# Configuration
# Updated default port to 8080 to match API server
API_URL = os.getenv("API_URL", "http://127.0.0.1:8080")

# Page Configuration
st.set_page_config(
    page_title="GroAI.01 Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #191C29;
    }
    .stApp {
        background: radial-gradient(circle at 50% 50%, #1e2235 0%, #191C29 100%);
    }
    .css-1d391kg {
        background-color: #212533;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #EA580C;
        color: white;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #f97316;
        box-shadow: 0 4px 15px rgba(234, 88, 12, 0.4);
    }
    /* Tab Header Styling */
    button[data-baseweb="tab"] {
        font-size: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Helper for safe float conversion
def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

# Initialize session state for persistent results
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

# --- Header ---
st.title("🚀 GroAI.01 - AI Signal Mapping")
st.markdown("""
<div style="padding: 10px; border-radius: 5px; background: rgba(234, 88, 12, 0.1); border-left: 5px solid #EA580C; margin-bottom: 20px;">
    <strong>AI-Driven Alpha Generation:</strong> This dashboard visualizes projected returns by synthesizing LLM sentiment, historical pattern matching, and machine learning models.
</div>
""", unsafe_allow_html=True)

# --- Sidebar Inputs ---
st.sidebar.markdown(
    '<a href="https://aihedge.finance" target="_blank">'
    '<img src="https://www.aihedge.finance/images/logo/logo2.png" width="150">'
    '</a>',
    unsafe_allow_html=True
)
st.sidebar.header("Control Panel")
analyze_top = st.sidebar.button("Analyze Signal", type="primary", key="top_analyze")
prompt = st.sidebar.text_input("Signal Prompt", value="bullish momentum", help="Textual context for the LLM analysis")

# Dynamic Feature Loading
feature_names_history = []
feature_names_model = []
defaults_loaded = False

try:
    # Attempt to fetch feature names from the running API
    response = requests.get(f"{API_URL}/ai/features", timeout=2.0)
    if response.status_code == 200:
        data = response.json()
        feature_names_history = data.get("history_features", [])
        feature_names_model = data.get("model_features", [])
        defaults_loaded = True
        st.sidebar.success(f"✅ Connected: {len(feature_names_history)} features loaded")
    else:
        st.sidebar.warning(f"⚠️ API status {response.status_code}. Using fallback.")
except Exception:
    st.sidebar.error("❌ API Offline. Using demo feature set.")

# Fallback defaults if API not reachable
if not defaults_loaded or not feature_names_history:
    feature_names_history = [f"Feature {i+1}" for i in range(4)]
    feature_names_model = ["ema_10", "ema_50", "rsi", "macd"]
    
# 1. Feature Vector Section (Ordered List for History)
st.sidebar.subheader("Feature Context")
feature_values = []

with st.sidebar.expander("History Features (Normalized)", expanded=True):
    # Enforce order as per API requirement
    for i, name in enumerate(feature_names_history):
        # Determine slider range and default based on feature type
        min_v, max_v, default_v = 0.0, 1.0, 0.5
        
        if "rsi" in name.lower():
            min_v, max_v, default_v = 0.0, 1.0, 0.05
        elif "ema_10" in name.lower(): # Ratio ~ 1.0
            min_v, max_v, default_v = 0.8, 1.2, 0.96
        elif "ema_50" in name.lower(): # Diff ~ 0.0
            min_v, max_v, default_v = -0.3, 0.3, -0.04
        elif "macd" in name.lower():   # Diff ~ 0.0 (smaller)
            min_v, max_v, default_v = -0.15, 0.15, -0.04
            
        val = st.slider(f"{name}", min_v, max_v, default_v, key=f"hist_{i}")
        feature_values.append(val)

# 2. Technicals Section (Dict for Model)
tech_data = {}
with st.sidebar.expander("Model Technicals", expanded=True):
    for i, name in enumerate(feature_names_model):
        default_val = 0.0
        # Set defaults based on optimization (Best found return: 0.02926)
        if "rsi" in name.lower():
            default_val = 47.70 
        elif "ema_10" in name.lower():
            default_val = 0.91
        elif "ema_50" in name.lower():
            default_val = -0.09
        elif "macd" in name.lower(): 
            default_val = -0.45
            
        val = st.number_input(f"{name}", value=default_val, step=0.01, key=f"tech_{i}")
        tech_data[name] = val

# Payload construction
# History features must be an ordered list
# Model technicals must be a dictionary
payload = {
    "prompt": prompt,
    "feature_values": feature_values, 
    "technicals": tech_data
}

# Analysis Action
analyze_bottom = st.sidebar.button("Analyze Signal", type="primary", key="bottom_analyze")

if analyze_top or analyze_bottom:
    with st.spinner("🧠 Processing Inference..."):
        try:
            response = requests.post(f"{API_URL}/ai/signal_analysis", json=payload, timeout=10.0)
            
            if response.status_code == 200:
                st.session_state.analysis_result = response.json()
                st.toast("Inference complete!", icon="✅")
            else:
                st.sidebar.error(f"Server Error ({response.status_code})")
                try:
                    st.sidebar.json(response.json())
                except:
                    st.sidebar.write(response.text[:200])
        except Exception as e:
            st.sidebar.error(f"Connection Error: {e}")

# --- Display Results ---
if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    
    # Extract values safely
    llm_out = result.get("llm_output", {})
    ret_history = safe_float(result.get("expected_return_from_history", 0.0))
    ret_model = safe_float(result.get("expected_return_from_model", 0.0))
    
    ret_llm = 0.0
    llm_comment = ""
    if isinstance(llm_out, dict):
        ret_llm = safe_float(llm_out.get("expected_return", 0.0))
        llm_comment = llm_out.get("comment", "")
    
    # Metrics Row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("LLM Prediction", f"{ret_llm*100:.2f}%")
    with c2:
        st.metric("History Match", f"{ret_history*100:.2f}%")
    with c3:
        st.metric("Model Logic", f"{ret_model*100:.2f}%")

    # Detailed Analysis
    tab1, tab2 = st.tabs(["📊 Performance Comparison", "🤖 AI Insight"])
    
    with tab1:
        st.subheader("Expected Return Distribution")
        fig, ax = plt.subplots(figsize=(10, 4))
        plt.style.use('dark_background')
        
        sources = ["LLM", "History", "Model"]
        values = [ret_llm * 100, ret_history * 100, ret_model * 100]
        colors = ["#4caf50" if v > 0 else "#f44336" for v in values] # Dynamic colors (Green for positive)
        
        bars = ax.bar(sources, values, color=colors, alpha=0.8, edgecolor='white', linewidth=0.5)
        ax.set_facecolor('#191C29')
        fig.patch.set_facecolor('#191C29')
        
        ax.set_title("Synthesis of Projected Returns", color='white', pad=20)
        ax.set_ylabel("Expected Return (%)", color='white')
        ax.axhline(0, color='white', linewidth=1, alpha=0.5)
        
        # Explicitly set axis colors to white
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')
        
        # Gridlines
        ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)
        
        # Labels
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:.2f}%',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3 if height >= 0 else -13),
                        textcoords="offset points",
                        color='white', ha='center', va='bottom' if height >= 0 else 'top',
                        fontweight='bold')

        st.pyplot(fig)

    with tab2:
        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.image("https://img.icons8.com/fluency/144/robot-2.png")
        with col_b:
            if llm_comment:
                st.info(f"**AI Commentary:**\n\n{llm_comment}")
            else:
                st.warning("No signal commentary provided by the model.")
            
            with st.expander("Raw Signal Data"):
                st.json(result)
else:
    # Landing state
    st.info("👈 Configure features in the sidebar and click **Analyze Signal** to begin investigation.")
    
    # Placeholder layout to show potential
    st.image("https://img.icons8.com/fluency/48/info.png", width=30)
    st.write("Awaiting user input for cross-modular alpha synthesis.")
