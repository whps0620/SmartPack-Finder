import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# --- PAGE CONFIG ---
st.set_page_config(page_title="SmartPack Finder", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_all_data():
    # 1. Load Materials
    df_mat = pd.read_csv('materials.csv') # Using your specific file name
    df_mat.columns = df_mat.columns.str.strip()
    
    # 2. Load Food Requirements
    df_food = pd.read_csv('food_requirements.csv')
    df_food.columns = df_food.columns.str.strip()
    
    # Pre-processing Materials
    df_mat['OTR_Updated_Num'] = pd.to_numeric(df_mat['OTR_Updated_Num'], errors='coerce')
    df_mat['WVTR_Updated_Num'] = pd.to_numeric(df_mat['WVTR_Updated_Num'], errors='coerce')
    df_mat = df_mat.dropna(subset=['OTR_Updated_Num', 'WVTR_Updated_Num'])
    
    # Classification for sustainability
    conventional = ['polypropylene', 'polyethylene', 'ldpe', 'hdpe', 'pet', 'evoh', 'pp', 'pe']
    df_mat['Material_Class'] = df_mat['Base Material'].apply(
        lambda x: 'Conventional' if str(x).lower().strip() in conventional else 'Sustainable'
    )
    
    return df_mat, df_food

df_mat, df_food = load_all_data()

# --- CLUSTERING ---
def get_clusters(data):
    # Log transform for better clustering on wide-range permeability data
    features = np.log10(data[['OTR_Updated_Num', 'WVTR_Updated_Num']] + 1e-5)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    db = DBSCAN(eps=0.5, min_samples=3).fit(scaled)
    return db.labels_

df_mat['Cluster'] = get_clusters(df_mat)

# --- UI LAYOUT ---
st.title("SmartPack Finder: Material Permeability Map")
st.markdown("Comparing **Material Performance** against **Food Requirements**")

col1, col2 = st.columns([3, 1])

with col1:
    fig = go.Figure()

    # 1. Draw Food Requirement Blocks (The Targets)
    for _, row in df_food.iterrows():
        # Create a rectangle for each food category
        fig.add_trace(go.Scatter(
            x=[row['min_wvtr'], row['max_wvtr'], row['max_wvtr'], row['min_wvtr'], row['min_wvtr']],
            y=[row['min_otr'], row['min_otr'], row['max_otr'], row['max_otr'], row['min_otr']],
            fill="toself",
            name=f"REQ: {row['Food Category']}",
            opacity=0.2,
            line=dict(width=1),
            legendgroup="Food Requirements"
        ))

    # 2. Plot Materials by Cluster
    for cluster in sorted(df_mat['Cluster'].unique()):
        c_data = df_mat[df_mat['Cluster'] == cluster]
        cluster_name = f"Cluster {cluster}" if cluster != -1 else "Noise/Variable"
        
        fig.add_trace(go.Scatter(
            x=c_data['WVTR_Updated_Num'],
            y=c_data['OTR_Updated_Num'],
            mode='markers',
            name=cluster_name,
            text=c_data['Base Material'] + " (" + c_data['Type'] + ")",
            marker=dict(size=10, opacity=0.8),
            hovertemplate="<b>%{text}</b><br>OTR: %{y} cm³/m²·day<br>WVTR: %{x} g/m²·day<extra></extra>"
        ))

    # Units and Formatting
    fig.update_xaxes(type="log", title="WVTR (g/m²·day)", gridcolor='lightgray')
    fig.update_yaxes(type="log", title="OTR (cm³/m²·day)", gridcolor='lightgray')
    fig.update_layout(height=700, template="plotly_white", legend_title="Categories")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Filter & Analysis")
    show_sustainable = st.toggle("Show only Sustainable Materials", value=False)
    
    target_food = st.selectbox("Highlight Food Needs", df_food['Food Category'].unique())
    food_row = df_food[df_food['Food Category'] == target_food].iloc[0]
    
    st.info(f"**Target for {target_food}:**\n"
            f"- OTR: {food_row['min_otr']} to {food_row['max_otr']} cm³/m²·day\n"
            f"- WVTR: {food_row['min_wvtr']} to {food_row['max_wvtr']} g/m²·day")
    
    # Filtered Results Table
    display_df = df_mat.copy()
    if show_sustainable:
        display_df = display_df[display_df['Material_Class'] == 'Sustainable']
    
    # Matching logic
    matches = display_df[
        (display_df['OTR_Updated_Num'] >= food_row['min_otr']) & 
        (display_df['OTR_Updated_Num'] <= food_row['max_otr']) &
        (display_df['WVTR_Updated_Num'] >= food_row['min_wvtr']) & 
        (display_df['WVTR_Updated_Num'] <= food_row['max_wvtr'])
    ]
    
    st.write(f"### Suitable { 'Sustainable' if show_sustainable else '' } Materials:")
    if not matches.empty:
        st.dataframe(matches[['Base Material', 'Secondary Material', 'Type']], hide_index=True)
    else:
        st.warning("No exact matches found for this category.")