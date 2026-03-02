import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Page Config
st.set_page_config(page_title="Sustainable Packaging Selector", layout="wide")

@st.cache_data  # This makes the app snappy on mobile!
# --- DATA LOADING FUNCTION ---
def load_and_clean_data():
    try:
        m_df = pd.read_csv('materials_permeability.csv')
        f_df = pd.read_csv('food_requirements.csv')
        
        m_df.columns = m_df.columns.str.strip()
        f_df.columns = f_df.columns.str.strip()
        
        group_cols = ['Base Material', 'Type', 'Secondary Material']
        agg_dict = {'OTR': 'max', 'WVTR': 'max'}
        
        unit_cols = [c for c in ['OTR_unit', 'WVTR_unit'] if c in m_df.columns]
        for c in unit_cols:
            agg_dict[c] = 'first'
        
        m_df_merged = m_df.groupby(group_cols).agg(agg_dict).reset_index()
        m_df_merged = m_df_merged.dropna(subset=['OTR', 'WVTR'])
        m_df_merged[['OTR', 'WVTR']] = m_df_merged[['OTR', 'WVTR']].replace(0, 0.0001)
        
        return m_df_merged, f_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

m_df, f_df = load_and_clean_data()

# --- TOP SECTION: PROJECT INFO ---
st.title("🌱 Sustainable Packaging Materials Recommendation Tool")
st.markdown("""
### About the Project
This tool is based on the research **'Mapping Gas Permeability of Sustainable Packaging Materials to Link Food Barrier Needs by Clustering Algorithms'**. 
The study addresses environmental concerns of conventional plastics by identifying sustainable alternatives that meet specific food preservation requirements. 
By classifying materials based on **Oxygen Transmission Rate (OTR)** and **Water Vapor Transmission Rate (WVTR)**, this framework helps match the right sustainable material to the unique barrier needs of different food categories.
""")

if m_df is not None and not m_df.empty:
    # Extract Units
    OTR_UNIT = m_df['OTR_unit'].iloc[0] if 'OTR_unit' in m_df.columns else "cc/m²·day"
    WVTR_UNIT = m_df['WVTR_unit'].iloc[0] if 'WVTR_unit' in m_df.columns else "g/m²·day"

    # --- Sidebar Requirements ---
    st.sidebar.header("📋 User Requirements")
    input_mode = st.sidebar.radio("Input Method", ["Select Food Category", "Manual Entry"])
    
    if input_mode == "Select Food Category":
        cat_col = [c for c in f_df.columns if c.lower() == 'food_category'][0]
        selected_name = st.sidebar.selectbox("Choose Category", f_df[cat_col].unique())
        food_row = f_df[f_df[cat_col] == selected_name].iloc[0]
        
        req_otr_min, req_otr_max = food_row['Min_OTR'], food_row['Max_OTR']
        req_wvtr_min, req_wvtr_max = food_row['Min_WVTR'], food_row['Max_WVTR']
        
        if 'Description' in food_row and pd.notna(food_row['Description']):
            st.sidebar.info(f"**Requirement Logic:** {food_row['Description']}")
    else:
        selected_name = "Custom Selection"
        c1, c2 = st.sidebar.columns(2)
        req_otr_min = c1.number_input(f"Min OTR ({OTR_UNIT})", value=0.1)
        req_otr_max = c2.number_input(f"Max OTR ({OTR_UNIT})", value=100.0)
        req_wvtr_min = c1.number_input(f"Min WVTR ({WVTR_UNIT})", value=0.1)
        req_wvtr_max = c2.number_input(f"Max WVTR ({WVTR_UNIT})", value=10.0)

    # --- K-Means Clustering ---
    scaler = StandardScaler()
    m_scaled = scaler.fit_transform(np.log10(m_df[['OTR', 'WVTR']])) 
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    m_df['Cluster'] = [f"Cluster {l+1}" for l in kmeans.fit_predict(m_scaled)]
    rep_materials = m_df.groupby('Cluster')['Base Material'].agg(lambda x: x.mode()[0]).to_dict()

    # --- Visualization ---
    fig = go.Figure()
    fig.add_shape(type="rect", x0=req_wvtr_min, x1=req_wvtr_max, y0=req_otr_min, y1=req_otr_max,
                  fillcolor="rgba(76, 175, 80, 0.15)", line=dict(color="#2E7D32", width=2))

    for cluster in sorted(m_df['Cluster'].unique()):
        data = m_df[m_df['Cluster'] == cluster]
        fig.add_trace(go.Scatter(
            x=data['WVTR'], y=data['OTR'], mode='markers', 
            name=f"{cluster} (Rep: {rep_materials[cluster]})",
            marker=dict(size=12, line=dict(width=1, color='white')),
            customdata=data[['Base Material', 'Secondary Material', 'Type']],
            hovertemplate="<b>%{customdata[0]}</b><br>Sec: %{customdata[1]}<br>Type: %{customdata[2]}<extra></extra>"
        ))

    fig.update_xaxes(type="log", title=f"WVTR ({WVTR_UNIT})", exponentformat="power")
    fig.update_yaxes(type="log", title=f"OTR ({OTR_UNIT})", exponentformat="power")
    fig.update_layout(template="plotly_white", title=f"<b>Permeability Mapping (25℃, RH50%): {selected_name}</b>")
    fig.update_layout(
        template="plotly_white", 
        title=f"<b>Permeability Mapping: {selected_name}</b>",
        # This keeps the legend readable on both Laptop and Mobile
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=-0.3, 
            xanchor="center", 
            x=0.5
        ),
        margin=dict(l=10, r=10, t=50, b=10) # Less "white space" on mobile
    )
    st.plotly_chart(fig, use_container_width=True) # Forces it to fit phone width

    # --- Abbreviations Note (Under Plot) ---
    with st.expander("ℹ️ Abbreviations & Material Definitions"):
        st.markdown("""
        * **Sec (Secondary Materials):** Additional components like montmorillonite, clay, or silica used to enhance material properties.
        * **Type:** How secondary materials interact with or modify the base material (e.g., nanocomposites, coatings, blends).
        * **Rep (Representative Materials):** The most common base material found in that cluster.
        * **Dataset Note:** The current dataset contains approximately 295 entries derived from 49 scientific studies (2000-2016). Given the current small scope, "Representative Materials" are illustrative and not yet fully representable[cite: 31, 259].
        """)

    # --- Results Table ---
    matches = m_df[(m_df['OTR'] >= req_otr_min) & (m_df['OTR'] <= req_otr_max) &
                    (m_df['WVTR'] >= req_wvtr_min) & (m_df['WVTR'] <= req_wvtr_max)]
    
    st.subheader(f"📋 Selection Results for {selected_name}")
    if not matches.empty:
        st.dataframe(matches[['Base Material', 'Secondary Material', 'Type', 'OTR', 'WVTR', 'Cluster']], use_container_width=True)
    else:
        st.warning("No materials fall within this exact range. Refer to 'Representative Materials' in the closest clusters.")

    # --- BOTTOM SECTION: CONTACT INFO ---
    st.divider()
    st.markdown("### 📞 Project Information")
    col1, col2 = st.columns(2) 
    with col1:
        st.write("**Student Name:**")
        st.write("Windy Yeh ([GitHub](https://github.com/whps0620/Food-Pack-Mapper/tree/main))") 
        st.write("**Supervisor Name:**")
        st.write("[Deniz Turan Kunter](https://research.wur.nl/en/persons/deniz-turan-kunter/)") 

    with col2:
        st.write("**Chair Group:**")
        st.write("[Food Quality and Design (FQD), Wageningen University & Research](https://www.wur.nl/en/chair-groups/food-sciences-and-technology/food-quality-and-design)")
        
    
    # --- ACADEMIC REFERENCES SECTION ---
    st.markdown("### 📚 Academia References")
    st.markdown("""
    **Food Permeability Requirements:**
    * Wang, J., Gardner, D. J., Stark, N. M., Bousfield, D. W., Tajvidi, M., & Cai, Z. (2018). Moisture and oxygen barrier properties of cellulose nanomaterial-based films. *ACS Sustainable Chemistry & Engineering, 6(1), 49–70*. [View Article](https://pubs.acs.org/doi/10.1021/acssuschemeng.7b03523)
    * Trinh, B. M.,Chang, B. P. & Mekonnen, T. H. (2023). The barrier properties of sustainable multiphase and multicomponent packaging materials: A review. *Progress in Materials Science*. [View Article](https://www.sciencedirect.com/science/article/abs/pii/S0079642523000038)

    **Material Permeability Dataset:**
    * Lentschat, M., Buche, P., Dibie-Barthélemy, J., Roche, M., et al. (2021). Food packaging permeability and composition dataset dedicated to text-mining. *Data in Brief, 36(4), 107135.*. [View Article](https://doi.org/10.1016/j.dib.2023.109312)
    """)

else:
    st.info("Please verify that 'materials_permeability.csv' and 'food_requirements.csv' are in your directory.")