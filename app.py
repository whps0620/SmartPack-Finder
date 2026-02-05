import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="SmartPack Finder", layout="wide", page_icon="📦")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    path = 'data/semi-processed_2.csv'
    if not os.path.exists(path):
        st.error(f"File not found at {path}. Please check your directory structure.")
        return pd.DataFrame()
    
    df = pd.read_csv(path)
    # Clean column names and convert to numeric
    df.columns = df.columns.str.strip()
    df['OTR_Updated_Num'] = pd.to_numeric(df['OTR_Updated_Num'], errors='coerce')
    df['WVTR_Updated_Num'] = pd.to_numeric(df['WVTR_Updated_Num'], errors='coerce')
    
    # Feature Engineering
    df['thickness_Updated_Num'] = df['thickness_Updated_Num'].fillna(0.0001)
    # Add small epsilon to avoid log(0)
    df['log_OTR'] = np.log10(df['OTR_Updated_Num'] + 1e-5)
    df['log_WVTR'] = np.log10(df['WVTR_Updated_Num'] + 1e-5)
    
    # Material Classification (Case-insensitive)
    conventional = ['polypropylene', 'polyethylene', 'ldpe', 'hdpe', 'pet', 'evoh']
    df['Material_Class'] = df['Base Material'].apply(
        lambda x: 'conventional' if str(x).lower().strip() in conventional else 'sustainable'
    )
    return df

# --- CLUSTERING LOGIC ---
def apply_clustering(df):
    features = df[['log_OTR', 'log_WVTR']].dropna()
    if features.empty:
        return df.assign(Cluster=-1)
    
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    # Parameters from your thesis
    db = DBSCAN(eps=1.17, min_samples=4).fit(scaled)
    
    features['Cluster'] = db.labels_
    # Join back to main dataframe
    return df.join(features['Cluster'], how='left').fillna({'Cluster': -1})

# --- FOOD REQUIREMENTS ---
food_reqs = {
    "Fruit, vegetable, and salads": {"min_otr": 1e4, "max_otr": 1e9, "min_wvtr": 1e2, "max_wvtr": 1e4, "color": "#2ecc71"},
    "Bakery": {"min_otr": 1e1, "max_otr": 1e3, "min_wvtr": 5, "max_wvtr": 1e2, "color": "#f1c40f"},
    "Cheese": {"min_otr": 1, "max_otr": 1e2, "min_wvtr": 1, "max_wvtr": 1e2, "color": "#f39c12"},
    "Meat": {"min_otr": 0.1, "max_otr": 50, "min_wvtr": 0.1, "max_wvtr": 20, "color": "#e74c3c"},
    "Peanuts": {"min_otr": 0.1, "max_otr": 10, "min_wvtr": 0.1, "max_wvtr": 10, "color": "#a0522d"},
    "Seafoods, meat": {"min_otr": 0.1, "max_otr": 50, "min_wvtr": 0.1, "max_wvtr": 10, "color": "#3498db"},
    "Coffee": {"min_otr": 0.01, "max_otr": 1, "min_wvtr": 0.01, "max_wvtr": 1, "color": "#34495e"},
    "Baby food": {"min_otr": 0.01, "max_otr": 1, "min_wvtr": 0.01, "max_wvtr": 1, "color": "#9b59b6"},
}

# --- APP LAYOUT ---
df_raw = load_data()

# --- SIDEBAR: REFINED INPUTS ---
st.sidebar.header("User Requirements")
if not df_raw.empty:
    df_plot = apply_clustering(df_raw)
    
    selected_food = st.sidebar.selectbox("1. Target Food Category", list(food_reqs.keys()))

    # Storage impact on requirements
    storage = st.sidebar.selectbox("2. Storage Condition", ["Ambient", "Refrigerated", "High Humidity"])
    special_reqs = st.sidebar.multiselect("3. Special Requirements", ["High Transparency", "High Heat Resistance", "Recyclable Content"])

    # Adjust requirements based on storage (Example logic for your thesis)
    req = food_reqs[selected_food].copy()
    if storage == "High Humidity":
        req['max_wvtr'] = req['max_wvtr'] * 0.5  # Make WVTR requirement 50% stricter
    elif storage == "Refrigerated":
        req['max_otr'] = req['max_otr'] * 0.8   # Make OTR slightly stricter

    
    # --- MAIN VISUALIZATION ---
    st.title("SmartPack Finder: Integrated Decision Tool")
    
    col1, col2 = st.columns([3, 1])
    
    # --- FILTERING & PLOTTING ---
    with col1:
        fig = go.Figure()

        # Draw the specific target zone
        fig.add_shape(type="rect",
            x0=req['min_wvtr'], x1=req['max_wvtr'], y0=req['min_otr'], y1=req['max_otr'],
            line=dict(color="RoyalBlue", width=3), fillcolor="LightSkyBlue", opacity=0.5
        )

        # Filter Sustainable Matches
        matches = df_plot[
            (df_plot['OTR_Updated_Num'] >= req['min_otr']) & (df_plot['OTR_Updated_Num'] <= req['max_otr']) &
            (df_plot['WVTR_Updated_Num'] >= req['min_wvtr']) & (df_plot['WVTR_Updated_Num'] <= req['max_wvtr']) &
            (df_plot['Material_Class'] == 'sustainable')
        ]

        # Plot all materials (background)
        fig.add_trace(go.Scatter(
            x=df_plot['WVTR_Updated_Num'], y=df_plot['OTR_Updated_Num'],
            mode='markers', name='Other Materials',
            marker=dict(color='lightgray', size=5),
            hoverinfo='skip'
        ))

        # Plot specifically the SUSTAINABLE matches with labels
        if not matches.empty:
            fig.add_trace(go.Scatter(
                x=matches['WVTR_Updated_Num'], y=matches['OTR_Updated_Num'],
                mode='markers+text', 
                name='Recommended Sustainable',
                text=matches['Base Material'],
                textposition="top center",
                marker=dict(color='green', size=12, symbol='star'),
            ))

        fig.update_xaxes(type="log", title="WVTR (g/m²·day)")
        fig.update_yaxes(type="log", title="OTR (cm³/m²·day)")
        st.plotly_chart(fig, use_container_width=True)
        
        # 2. Add Material Clusters
        for cluster in df_plot['Cluster'].unique():
            c_data = df_plot[df_plot['Cluster'] == cluster]
            name = f"Cluster {int(cluster)}" if cluster != -1 else "Noise/Outliers"
            fig.add_trace(go.Scatter(
                x=c_data['WVTR_Updated_Num'], 
                y=c_data['OTR_Updated_Num'],
                mode='markers', 
                name=name,
                text=c_data['Base Material'],
                marker=dict(size=8, opacity=0.8),
                legendgroup="Materials"
            ))

        fig.update_xaxes(type="log", title="WVTR (g/m²·day)", range=[-2, 7])
        fig.update_yaxes(type="log", title="OTR (cm³/m²·day)", range=[-2, 10])
        fig.update_layout(height=700, template="plotly_white", legend_title="Legend")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Results")
        # Filter logic
        matches = df_plot[
            (df_plot['OTR_Updated_Num'] >= req['min_otr']) & (df_plot['OTR_Updated_Num'] <= req['max_otr']) &
            (df_plot['WVTR_Updated_Num'] >= req['min_wvtr']) & (df_plot['WVTR_Updated_Num'] <= req['max_wvtr'])
        ]
        
        sustainable_matches = matches[matches['Material_Class'] == 'sustainable']

        if not sustainable_matches.empty:
            st.success(f"Found {len(sustainable_matches)} Sustainable Materials")
            st.dataframe(sustainable_matches[['Base Material', 'Type']], hide_index=True)
        elif not matches.empty:
            st.info("No sustainable matches, but conventional materials found.")
            st.dataframe(matches[['Base Material', 'Type']].head(5), hide_index=True)
        else:
            st.warning("No exact matches found in the database.")
            st.write("Consider checking **Cluster 0** for high-barrier options.")
else:
    st.error("Application could not load data. Check 'data/semi-processed_2.csv'.")