import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="SmartPack Finder", layout="wide")

# --- DATA LOADING & CLEANING (Based on your Notebook) ---
@st.cache_data
def load_data():
    # Load your semi-processed data
    df = pd.read_csv('data/semi-processed_2.csv')
    
    # Standardizing names and filling missing values as per your EDA
    df['Type'] = df['Type'].replace('Individual', 'individual')
    df['Secondary Material'] = df['Secondary Material'].fillna('None')
    df['Composition'] = df['Composition'].fillna('None')
    
    # Fill missing thickness if not provided
    df['thickness_Updated_Num'] = df['thickness_Updated_Num'].fillna(0.0001)
    
    # Filter for sustainable materials vs conventional
    conventional_list = [
        'polypropylene', 'polyethylene', 'polyvinyl chloride', 'LDPE', 
        'HDPE', 'poly(n-butyl methacrylate)', 'polyethylene terephthalate', 
        'EVOH', 'polysulfone'
    ]
    df['Material_Class'] = df['Base Material'].apply(
        lambda x: 'conventional' if str(x).lower() in conventional_list else 'sustainable'
    )
    
    return df

df = load_data()

# --- APP UI ---
st.title("SmartPack Finder 🎈")
st.markdown("Matching food requirements with sustainable packaging via permeability.")

# Sidebar for Inputs
st.sidebar.header("Step 1: Define Food Needs")

food_cat = st.sidebar.selectbox(
    "Food Category", 
    ["Fresh Produce (High O2 needed)", "High-fat/Cheese (Low O2 needed)", "Dry Goods (Low WVTR needed)"]
)

st.sidebar.markdown("---")
st.sidebar.header("Step 2: Set Permeability Thresholds")

# User can manually override or use presets based on category
target_otr = st.sidebar.number_input("Max OTR (cm³/m²·day)", value=100.0)
target_wvtr = st.sidebar.number_input("Max WVTR (g/m²·day)", value=50.0)

# --- MATCHING LOGIC ---
st.header("Materials Suggestion")

# Filtering materials that meet the OTR and WVTR requirements
# Using 'OTR_Updated_Num' and 'WVTR_Updated_Num' from your FE notebook
matched_df = df[
    (df['OTR_Updated_Num'] <= target_otr) & 
    (df['WVTR_Updated_Num'] <= target_wvtr) &
    (df['Material_Class'] == 'sustainable')
].copy()

if not matched_df.empty:
    st.success(f"Found {len(matched_df)} sustainable materials matching your requirements!")
    
    # Select columns to display
    display_cols = [
        'Base Material', 'Secondary Material', 'Type', 
        'OTR_Updated_Num', 'WVTR_Updated_Num', 'thickness_Updated_Num'
    ]
    
    # Rename for clarity in UI
    final_table = matched_df[display_cols].rename(columns={
        'OTR_Updated_Num': 'OTR (cm³/m²·day)',
        'WVTR_Updated_Num': 'WVTR (g/m²·day)',
        'thickness_Updated_Num': 'Thickness (m)'
    })
    
    st.dataframe(final_table, use_container_width=True)
    
    # Visualize the matches
    st.subheader("Performance Comparison")
    st.scatter_chart(final_table, x='OTR (cm³/m²·day)', y='WVTR (g/m²·day)', color='Base Material')

else:
    st.warning("No sustainable materials found for these specific requirements. Try increasing the thresholds.")

# --- SUSTAINABILITY INFO ---
with st.expander("Why this matters?"):
    st.write("""
        Matching permeability correctly reduces food waste. By selecting a 'sustainable' class material 
        instead of a 'conventional' one (like LDPE or PET), you reduce the carbon footprint 
        of the packaging while maintaining shelf-life.
    """)