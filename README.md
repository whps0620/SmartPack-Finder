# 🌱 Food-Pack-Mapper: Sustainable Packaging Selector

An interactive decision-support tool designed to match sustainable packaging materials with the specific permeability requirements of various food categories. This tool was developed at **Wageningen University & Research** to bridge the gap between material science and food quality design.

## 🚀 Key Features
* **Log-Log Performance Mapping:** Visualizes Oxygen Transmission Rate (OTR) vs. Water Vapor Transmission Rate (WVTR) on scientific power scales ($10^x$) to handle a wide range of barrier properties.
* **Fixed 4-Tier Clustering:** Uses K-Means clustering to categorize materials into four distinct performance tiers, identifying "Representative Materials" for each tier.
* **Smart Requirement Matching:** Displays a visual "Safe Zone" (Green Box) based on the specific needs of selected food categories.
* **Contextual Logic:** Provides specific descriptions for food categories (e.g., moisture requirements for bakery items to prevent sogginess).
* **Data-Driven Insights:** Analyzes a consolidated dataset of sustainable material profiles.

## 🛠️ Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/whps0620/Food-Pack-Mapper.git](https://github.com/whps0620/Food-Pack-Mapper.git)
   cd Food-Pack-Mapper
   ```


2. **Install dependencies:**
    ```bash 
    pip install streamlit pandas numpy plotly scikit-learn
    ```

3. **Run the application locally:**
    ```bash
    streamlit run app.py
    ```

## 📊 Data Sources & Academic References
The data and logic used in this tool are based on the following peer-reviewed publications:

### Food Requirements & Barrier Logic
* Wang, J., & Gardner, D. J. (2017). Moisture and oxygen barrier properties of cellulose nanomaterial-based films. ACS Applied Materials & Interfaces, 9(34), 28111-28131. https://doi.org/10.1021/acsami.7b01010

* Trinh, B. M., & Mekonnen, T. H. (2022). The barrier properties of sustainable multiphase and multicomponent packaging materials: A review. Progress in Materials Science, 129, 100937. https://doi.org/10.1016/j.pmatsci.2022.100937

### Material Permeability Dataset
* Lentschat, M., & Valat, A. (2023). Food packaging permeability and composition dataset dedicated to text-mining. Data in Brief, 48, 109312. https://doi.org/10.1016/j.dib.2023.109312

## 📞 Project Information
* Student: Windy Yeh
* Supervisor: Deniz Turan Kunter
* Chair Group: Food Quality and Design (FQD), Wageningen University & Research (WUR)