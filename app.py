import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# --- PAGE CONFIG ---
st.set_page_config(page_title="SmartPack Finder", layout="wide")

# --- DATA LOADING & CLEANING ---
@st.cache_data
def load_and_preprocess_data():
    # Load your semi-processed dataset
    df = pd.read_csv('data/semi-processed_2.csv')
    
    # Cleaning based on your EDA notebook
    df['Type'] = df['Type'].replace('Individual', 'individual')
    df['Secondary Material'] = df['Secondary Material'].fillna('None')
    df['thickness_Updated_Num'] = df['thickness_Updated_Num'].fillna(0.0001) # Default 100um
    
    # Conventional vs Sustainable classification
    conventional_list = [
        'polypropylene', 'polyethylene', 'polyvinyl chloride', 'LDPE', 
        'HDPE', 'polyethylene terephthalate', 'EVOH', 'polysulfone'
    ]
    df['Material_Class'] = df['Base Material'].apply(
        lambda x: 'conventional' if str(x).lower() in conventional_list else 'sustainable'
    )
    
    # Convert values to log scale for clustering (as seen in your FE notebook)
    # Adding small constant to avoid log(0)
    df['log_OTR'] = np.log10(df['OTR_Updated_Num'] + 1e-5)
    df['log_WVTR'] = np.log10(df['WVTR_Updated_Num'] + 1e-5)
    
    return df

df = load_and_preprocess_data()

# --- SIDEBAR: USER INPUTS ---
st.sidebar.header("Step 1: Food Requirements")

food_category = st.sidebar.selectbox(
    "Food Category",
    ["Fruit, vegetable, and salads", "Bakery", "Cheese", "Meat", "Peanuts", "Seafoods, meat", "Coffee", "Baby food"]
)

storage_condition = st.sidebar.selectbox(
    "Storage Condition",
    ["Ambient", "Refrigerated", "High Humidity", "Frozen"]
)

# Preset thresholds based on category (Scientific logic from your thesis)
presets = {
    "Fruit, vegetable, and salads": {"otr": 10**8, "wvtr": 10**2},
    "Cheese": {"otr": 10**1, "wvtr": 10**1},
    "Coffee": {"otr": 10**0, "wvtr": 10**0},
    "Meat": {"otr": 10**1, "wvtr": 10**1},
}
default = presets.get(food_category, {"otr": 100.0, "wvtr": 50.0})

target_otr = st.sidebar.number_input("Max OTR (cm³/m²·day)", value=float(default['otr']))
target_wvtr = st.sidebar.number_input("Max WVTR (g/m²·day)", value=float(default['wvtr']))

# --- ML CLUSTERING (DBSCAN) ---
# Using parameters from your thesis (eps=1.17, min_samples=4)
def apply_dbscan(data):
    features = data[['log_OTR', 'log_WVTR']].dropna()
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    dbscan = DBSCAN(eps=1.17, min_samples=4)
    labels = dbscan.fit_predict(scaled_features)
    
    features['Cluster'] = labels
    return features

# --- MAIN UI ---
st.title("SmartPack Finder 🎈")
st.markdown("Matching food requirements with sustainable packaging via DBSCAN clustering.")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Permeability Mapping (Thesis Page 18)")
    
    # Run clustering
    clustered_features = apply_dbscan(df)
    plot_df = df.join(clustered_features['Cluster'], how='inner')

    # Create Plotly Scatter (Log-Log Scale)
    fig = go.Figure()

    # Add Material Clusters
    for cluster in plot_df['Cluster'].unique():
        c_df = plot_df[plot_df['Cluster'] == cluster]
        name = f"Cluster {cluster}" if cluster != -1 else "Noise"
        fig.add_trace(go.Scatter(
            x=c_df['WVTR_Updated_Num'], y=c_df['OTR_Updated_Num'],
            mode='markers', name=name,
            text=c_df['Base Material'],
            marker=dict(size=8)
        ))

    # Add Food Need Zone (Highlight user selection)
    fig.add_shape(type="rect",
        x0=0.1, y0=0.1, x1=target_wvtr, y1=target_otr,
        line=dict(color="Red", width=2),
        fillcolor="LightSalmon", opacity=0.3
    )

    fig.update_xaxes(type="log", title="WVTR (g/m²·day)")
    fig.update_yaxes(type="log", title="OTR (cm³/m²·day)")
    fig.update_layout(height=600, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Matching Results")
    
    # Filtering materials based on inputs
    matches = df[
        (df['OTR_Updated_Num'] <= target_otr) & 
        (df['WVTR_Updated_Num'] <= target_wvtr) &
        (df['Material_Class'] == 'sustainable')
    ].sort_values('OTR_Updated_Num').head(10)

    if not matches.empty:
        st.success(f"Found {len(matches)} matches!")
        for i, row in matches.iterrows():
            with st.expander(f"✅ {row['Base Material']}"):
                st.write(f"**Type:** {row['Type']}")
                st.write(f"**OTR:** {row['OTR_Updated_Num']:.2f}")
                st.write(f"**WVTR:** {row['WVTR_Updated_Num']:.2f}")
    else:
        st.warning("No sustainable matches found for these exact constraints.")

# --- FOOTER ---
st.markdown("---")
st.info("Algorithm Metrics: DBSCAN Silhouette Score: 0.900 | Davies-Bouldin Index: 0.388")