import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="PetroVisual Pro", layout="wide")

# Custom CSS for a professional "Dark Mode" engineering look
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    stMarkdown { color: #fafafa; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛢️ PetroVisual Pro: Next-Gen Well Log Interpreter")
st.sidebar.header("Control Panel")

# --- STEP 1: UPLOAD DATA ---
uploaded_file = st.sidebar.file_uploader("Upload Log Data (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.sidebar.success("Log Data Loaded!")
    
    # Columns selection (Auto-detecting common names)
    columns = df.columns.tolist()
    depth_col = st.sidebar.selectbox("Select Depth Column", columns, index=0)
    gr_col = st.sidebar.selectbox("Select Gamma Ray (GR) Column", columns, index=1)
    
    # --- STEP 2: INTERPRETATION SETTINGS ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("Interpretation Parameters")
    gr_min = st.sidebar.number_input("GR Clean (Sand min)", value=float(df[gr_col].min()))
    gr_max = st.sidebar.number_input("GR Shale (Shale max)", value=float(df[gr_col].max()))
    cutoff = st.sidebar.slider("Sand/Shale Cutoff Line", min_value=float(gr_min), max_value=float(gr_max), value=75.0)

    # Calculate Vshale (Linear Method)
    df['Vshale'] = (df[gr_col] - gr_min) / (gr_max - gr_min)
    df['Vshale'] = df['Vshale'].clip(0, 1) # Keep values between 0 and 1

    # --- STEP 3: VISUALIZATION ---
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.metric("Avg Vshale", f"{df['Vshale'].mean():.2%}")
        st.metric("Net/Gross Ratio", f"{(df[gr_col] < cutoff).mean():.2%}")

    with col2:
        fig, ax = plt.subplots(1, 2, figsize=(10, 12), sharey=True)
        plt.subplots_adjust(wspace=0.1)

        # TRACK 1: Gamma Ray
        ax[0].plot(df[gr_col], df[depth_col], color='black', lw=1)
        ax[0].set_title("Gamma Ray (API)")
        ax[0].set_xlim(gr_min, gr_max)
        ax[0].grid(True, linestyle='--')
        ax[0].invert_yaxis()
        
        # Color Shading for Interpretation
        ax[0].fill_betweenx(df[depth_col], cutoff, df[gr_col], where=(df[gr_col] >= cutoff), color='grey', alpha=0.5, label='Shale')
        ax[0].fill_betweenx(df[depth_col], gr_min, df[gr_col], where=(df[gr_col] < cutoff), color='yellow', alpha=0.5, label='Sand')

        # TRACK 2: Vshale (Volume of Shale)
        ax[1].plot(df['Vshale'], df[depth_col], color='blue', lw=1.5)
        ax[1].fill_betweenx(df[depth_col], 0, df['Vshale'], color='blue', alpha=0.3)
        ax[1].set_title("Vshale (Fraction)")
        ax[1].set_xlim(0, 1)
        ax[1].grid(True, linestyle='--')

        st.pyplot(fig)

    # --- STEP 4: DOWNLOAD RESULTS ---
    st.markdown("### Export Processed Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV with Vshale Calculations", csv, "interpreted_logs.csv", "text/csv")

else:
    st.info("Welcome! Please upload an Excel file with Depth and Gamma Ray data to begin.")
    st.markdown("""
    **Required Columns:** - Depth (meters or feet)
    - GR (Gamma Ray values)
    """)
