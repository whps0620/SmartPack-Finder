import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Sustainable Packaging Selector", layout="wide")
st.title("🌱 Sustainable Packaging Recommendation Tool")

def load_and_clean_data():
    try:
        m_df = pd.read_csv('materials_permeability.csv')
        f_df = pd.read_csv('food_requirements.csv')
        
        m_df.columns = m_df.columns.str.strip()
        f_df.columns = f_df.columns.str.strip()
        
        # Merge OTR and WVTR rows into unique material profiles
        group_cols = ['Base Material', 'Type', 'Secondary Material']
        unit_cols = [c for c in ['OTR_unit', 'WVTR_unit'] if c in m_df.columns]
        
        m_df_merged = m_df.groupby(group_cols).agg({
            'OTR': 'max',
            'WVTR': 'max',
            **{c: 'first' for c in unit_cols}
        }).reset_index()

        # Remove profiles missing either value for clustering math
        m_df_merged = m_df_merged.dropna(subset=['OTR', 'WVTR'])
        
        return m_df_merged, f_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

m_df, f_df = load_and_clean_data()

if m_df is not None and not m_df.empty:
    OTR_UNIT = m_df['OTR_unit'].iloc[0] if 'OTR_unit' in m_df.columns else "cc/m²·day"
    WVTR_UNIT = m_df['WVTR_unit'].iloc[0] if 'WVTR_unit' in m_df.columns else "g/m²·day"

    # --- Sidebar Configuration ---
    st.sidebar.header("📋 Requirements")
    input_mode = st.sidebar.radio("Input Method", ["Select Food Category", "Manual Entry"])
    
    # K-Means Parameter
    st.sidebar.markdown("---")
    st.sidebar.header("🤖 Clustering Settings")
    n_clusters = st.sidebar.slider("Number of Performance Tiers (K)", 2, 8, 3)

    req_otr_min, req_otr_max = 0.0, 100.0
    req_wvtr_min, req_wvtr_max = 0.0, 10.0
    selected_name = "Custom Selection"

    if input_mode == "Select Food Category":
        cat_cols = [c for c in f_df.columns if c.lower() == 'food_category']
        if cat_cols:
            selected_name = st.sidebar.selectbox("Choose Category", f_df[cat_cols[0]].unique())
            food_row = f_df[f_df[cat_cols[0]] == selected_name].iloc[0]
            req_otr_min, req_otr_max = food_row['Min_OTR'], food_row['Max_OTR']
            req_wvtr_min, req_wvtr_max = food_row['Min_WVTR'], food_row['Max_WVTR']
    else:
        c1, c2 = st.sidebar.columns(2)
        req_otr_min = c1.number_input(f"Min OTR", value=0.0)
        req_otr_max = c2.number_input(f"Max OTR", value=100.0)
        req_wvtr_min = c1.number_input(f"Min WVTR", value=0.0)
        req_wvtr_max = c2.number_input(f"Max WVTR", value=10.0)

    # --- K-Means Clustering ---
    scaler = StandardScaler()
    m_scaled = scaler.fit_transform(m_df[['OTR', 'WVTR']])
    
    # Initialize and fit K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    m_df['Cluster_ID'] = kmeans.fit_predict(m_scaled)
    m_df['Cluster_Label'] = m_df['Cluster_ID'].apply(lambda x: f"Tier {x+1}")

    # --- Visualization (Log Scale) ---
    fig = go.Figure()
    
    # Requirement Block
    fig.add_shape(type="rect", x0=req_wvtr_min, x1=req_wvtr_max, y0=req_otr_min, y1=req_otr_max,
                  fillcolor="rgba(0, 255, 0, 0.15)", line=dict(color="Green", width=2))

    # Materials
    for cluster in sorted(m_df['Cluster_Label'].unique()):
        data = m_df[m_df['Cluster_Label'] == cluster]
        fig.add_trace(go.Scatter(
            x=data['WVTR'], y=data['OTR'], mode='markers', name=cluster,
            marker=dict(size=12, line=dict(width=1, color='white')),
            customdata=data[['Base Material', 'Secondary Material', 'Type']],
            hovertemplate="<b>%{customdata[0]}</b><br>Sec: %{customdata[1]}<br>Type: %{customdata[2]}<br>WVTR: %{x}<br>OTR: %{y}<extra></extra>"
        ))

    # UPDATE: Set axis types to 'log'
    fig.update_xaxes(type="log", exponentformat="power")
    fig.update_yaxes(type="log", exponentformat="power")

    fig.update_layout(
        title=f"Log-Scale Permeability: {selected_name}",
        xaxis_title=f"WVTR ({WVTR_UNIT})", 
        yaxis_title=f"OTR ({OTR_UNIT})", 
        template="plotly_white", 
        height=650
    )
    st.plotly_chart(fig, use_container_width=True)


    # --- Recommendation Table ---
    matches = m_df[
        (m_df['OTR'] >= req_otr_min) & (m_df['OTR'] <= req_otr_max) &
        (m_df['WVTR'] >= req_wvtr_min) & (m_df['WVTR'] <= req_wvtr_max)
    ]
    
    st.subheader(f"📋 Selection Results: {selected_name}")
    if not matches.empty:
        st.success(f"Found {len(matches)} matching materials.")
        st.table(matches[['Base Material', 'Secondary Material', 'Type', 'OTR', 'WVTR', 'Cluster_Label']])
    else:
        st.error("No exact matches found. Consider materials in the Tier closest to the green box.")

else:
    st.info("Check your CSV files. We need both OTR and WVTR values for the same material types to perform clustering.")