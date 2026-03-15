import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="PetroStream Ultra", layout="wide")

# Dark Mode UI Styling
plt.style.use('dark_background')

st.title("🛡️ PetroStream Ultra: Advanced Reservoir Analytics")
st.markdown("---")

# --- SIDEBAR CONTROL ---
st.sidebar.title("🛠️ Analysis Tools")
uploaded_file = st.sidebar.file_uploader("Upload Borehole Data", type=["xlsx", "csv"])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    
    # Column Mapping
    cols = df.columns.tolist()
    z_col = st.sidebar.selectbox("Depth", cols, index=0)
    gr_col = st.sidebar.selectbox("Gamma Ray", cols, index=1)
    res_col = st.sidebar.selectbox("Resistivity", cols, index=2 if len(cols)>2 else 1)

    # Physics Parameters
    st.sidebar.subheader("Petrophysical Cutoffs")
    gr_cutoff = st.sidebar.slider("GR Sand/Shale Cutoff", 0, 150, 75)
    res_cutoff = st.sidebar.slider("Resistivity Pay Cutoff (Ohm-m)", 0, 100, 20)

    # --- THE LOGIC ---
    # Determine Lithology
    df['Lithology'] = np.where(df[gr_col] < gr_cutoff, 1, 0) # 1 for Sand, 0 for Shale
    # Determine Pay Zone (Sand AND High Resistivity)
    df['Pay'] = np.where((df['Lithology'] == 1) & (df[res_col] > res_cutoff), 1, 0)

    # --- PLOTTING SECTION ---
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(12, 10), sharey=True)
    fig.patch.set_facecolor('#0e1117')

    # TRACK 1: Gamma Ray (Lithology)
    ax[0].plot(df[gr_col], df[z_col], color='lightgreen', lw=1.5)
    ax[0].fill_betweenx(df[z_col], gr_cutoff, df[gr_col], where=(df[gr_col] >= gr_cutoff), color='slategray', alpha=0.6)
    ax[0].fill_betweenx(df[z_col], 0, df[gr_col], where=(df[gr_col] < gr_cutoff), color='yellow', alpha=0.6)
    ax[0].set_title("Gamma Ray", color='white', weight='bold')
    ax[0].set_xlim(0, 150)
    ax[0].invert_yaxis()
    ax[0].grid(alpha=0.2)

    # TRACK 2: Lithology Ribbon (The "Pro" Look)
    # This creates a solid color bar showing where the sand and pay zones are
    ax[1].fill_betweenx(df[z_col], 0, 1, where=(df['Lithology'] == 0), color='slategray', alpha=0.9) # Shale
    ax[1].fill_betweenx(df[z_col], 0, 1, where=(df['Lithology'] == 1), color='yellow', alpha=0.9)    # Sand
    ax[1].fill_betweenx(df[z_col], 0, 1, where=(df['Pay'] == 1), color='red', alpha=0.8)             # PAY!
    ax[1].set_title("Lithology", color='white', weight='bold')
    ax[1].set_xticks([]) # Remove x-axis for a clean ribbon look

    # TRACK 3: Resistivity (Logarithmic Scale)
    ax[2].semilogx(df[res_col], df[z_col], color='cyan', lw=1.5)
    ax[2].axvline(x=res_cutoff, color='white', linestyle='--', alpha=0.5)
    ax[2].set_title("Resistivity", color='white', weight='bold')
    ax[2].grid(which='both', alpha=0.1)

    st.pyplot(fig)

    # --- STATS CARDS ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Net Sand (m)", f"{df['Lithology'].sum()} m")
    c2.metric("Net Pay (m)", f"{df['Pay'].sum()} m", delta="Potential Reservoir")
    c3.metric("Avg Resistivity", f"{df[res_col].mean():.2f} Ωm")

else:
    st.warning("Please upload a file to begin the analysis.")

# --- TECHNICAL INTELLIGENCE SECTION ---
with st.expander("📚 Technical Documentation & Petrophysical Logic"):
    st.markdown("""
    ### How PetroStream Ultra Detects Hydrocarbons
    This application utilizes a dual-track crossover logic to identify potential Net Pay zones:
    
    1. **Lithology Identification ($V_{sh}$):** We use the Gamma Ray index ($I_{GR}$) to distinguish between reservoir-quality sand and non-reservoir shale.
       $$I_{GR} = \frac{GR_{log} - GR_{min}}{GR_{max} - GR_{min}}$$
       *Zones below the user-defined **GR Cutoff** are classified as Sand.*

    2. **Fluid Discrimination (Resistivity):** Because hydrocarbons (Oil/Gas) are non-conductive, they increase the formation resistivity ($R_t$). 
       *If a Sand zone ($I_{GR} < Cutoff$) also displays high resistivity ($R_t > Cutoff$), it is flagged as a **Net Pay Zone**.*

    3. **The "Water Leg" Detection:** A unique feature of this tool is identifying "Wet Sands." If the app detects Sand but the Resistivity is low, it remains **Yellow**—indicating a potential water-bearing reservoir.
    """)
    
    st.info("📊 **Algorithm Note:** This tool currently uses a deterministic binary cutoff. Future updates will include Archie's Equation for Water Saturation ($S_w$) modeling.")
