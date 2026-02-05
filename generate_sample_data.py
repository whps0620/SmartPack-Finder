"""
Sample Data Generator for Material Analysis Pipeline
This script generates sample CSV files for testing the Streamlit application
"""

import pandas as pd
import numpy as np
from datetime import datetime

# Set random seed for reproducibility
np.random.seed(42)

def generate_rawdata(n_samples=100):
    """Generate sample rawdata.csv"""
    
    materials = ['PLA', 'LDPE', 'HDPE', 'PP', 'PET', 'chitosan', 'gelatin', 'starch']
    properties = ['OP', 'OTR', 'PCO2', 'WVP', 'WVTR']
    
    data = {
        'Doc': [f'Sample document about {np.random.choice(materials)} properties' for _ in range(n_samples)],
        'Material': np.random.choice(materials, n_samples),
        'Property': np.random.choice(properties, n_samples),
        'Value': np.random.uniform(0.1, 100, n_samples),
        'Unit': ['cm³·mm/(m²·day·atm)'] * n_samples,
        'Temperature': np.random.uniform(20, 40, n_samples),
        'Humidity': np.random.uniform(40, 90, n_samples)
    }
    
    df = pd.DataFrame(data)
    df.to_csv('rawdata.csv', index=False)
    print(f"✅ Generated rawdata.csv with {n_samples} samples")
    return df

def generate_golden_transmat(n_samples=50):
    """Generate goldenTRANSMAT-all.csv"""
    
    targets = ['OP', 'OTR', 'WVP', 'WVTR', 'PCO2']
    
    data = {
        'Doc': [f'Document {i+1}' for i in range(n_samples)],
        'Target': np.random.choice(targets, n_samples),
        'Value': np.random.uniform(0.1, 100, n_samples),
        'Annotator': ['consensus'] * n_samples
    }
    
    df = pd.DataFrame(data)
    df.to_csv('goldenTRANSMAT-all.csv', index=False)
    print(f"✅ Generated goldenTRANSMAT-all.csv with {n_samples} samples")
    return df

def generate_annotator_files(n_samples=40):
    """Generate annotator CSV files"""
    
    targets = ['OP', 'OTR', 'WVP', 'WVTR', 'PCO2']
    
    for i in range(1, 4):
        data = {
            'Doc': [f'Document {j+1}' for j in range(n_samples)],
            'Target': np.random.choice(targets, n_samples),
            'Value': np.random.uniform(0.1, 100, n_samples),
            'Annotator': [f'annotator{i}'] * n_samples
        }
        
        df = pd.DataFrame(data)
        df.to_csv(f'goldenTRANSMAT-annotator{i}.csv', index=False)
        print(f"✅ Generated goldenTRANSMAT-annotator{i}.csv with {n_samples} samples")

def generate_perm_data(n_samples=25):
    """Generate 22perm.csv with material titles"""
    
    titles = [
        'Barrier properties of chitosan coated polyethylene',
        'Gas permeation properties of poly(lactic acid)',
        'Water vapor permeability of methylcellulose-based edible films',
        'Oxygen barrier properties of starch films',
        'Gas transport properties of polypropylene clay composite membranes',
        'Barrier and surface properties of chitosan-coated greaseproof paper',
        'Tensile properties of PLA nanoclay composite films',
        'Effect of plasticizers on mechanical properties of chitosan films',
        'Gas barrier properties of nanocomposites based on montmorillonite',
        'Water vapor barrier performance of corn-zein coated polypropylene films',
        'Gas separation properties of polyether-based polyurethane-silica nanocomposite membranes',
        'Barrier and mechanical properties of carrot puree films',
        'Design of biodegradable bio-based films from poly-lactic acid',
        'Edible oxygen barrier bilayer film from corn zein and soy protein isolate',
        'Gas transfer properties of wheat gluten coated paper',
        'Antiplasticisation and oxygen permeability of starch-sorbitol films',
        'Application of bioplastics for food packaging',
        'Effect of clay content on mechanical properties of fish gelatin montmorillonite films',
        'Exploring potentialities of lignocellulosic fibres in biocomposites for food packaging',
        'Gas permeation properties of polypropylene nanocomposites with thermally-stable clay',
        'Suitability of novel galactomannans as edible coatings for tropical fruits',
        'Validation of a predictive model for gas transfer in modified atmosphere packaging',
        'Soluble soybean polysaccharide - biodegradable film for sustainable packaging',
        'Barrier properties of nylon 6-montmorillonite nanocomposite membranes prepared by melt blending',
        'Gas permeation and mechanical properties of PBAT composite films'
    ]
    
    # Use titles or generate random ones if n_samples > len(titles)
    if n_samples <= len(titles):
        selected_titles = titles[:n_samples]
    else:
        selected_titles = titles + [f'Additional material study {i}' for i in range(n_samples - len(titles))]
    
    data = {
        'doc': selected_titles,
        'permeability_value': np.random.uniform(0.1, 50, n_samples),
        'temperature': np.random.choice([23, 25, 30], n_samples),
        'humidity': np.random.choice([0, 50, 75, 90], n_samples)
    }
    
    df = pd.DataFrame(data)
    df.to_csv('22perm.csv', index=False)
    print(f"✅ Generated 22perm.csv with {n_samples} samples")
    return df

def generate_semi_processed(n_samples=100):
    """Generate semi-processed_2.csv for ML models"""
    
    base_materials = ['PLA', 'LDPE', 'HDPE', 'PP', 'PET', 'chitosan', 'gelatin', 'starch', 'methylcellulose', 'corn zein']
    material_types = ['individual', 'coated', 'nanocomposite', 'composite', 'blend']
    secondary_materials = ['None', 'montmorillonite', 'clay', 'nanoclay', 'silica', 'cellulose']
    compositions = ['None', 'single', 'binary', 'ternary']
    targets = ['OP', 'OTR', 'WVP', 'WVTR', 'PCO2']
    
    data = {
        'Base Material': np.random.choice(base_materials, n_samples),
        'Type': np.random.choice(material_types, n_samples),
        'Secondary Material': np.random.choice(secondary_materials, n_samples),
        'Composition': np.random.choice(compositions, n_samples),
        'Target': np.random.choice(targets, n_samples),
        'Value': np.random.uniform(0.1, 100, n_samples),
        'Temperature': np.random.uniform(20, 40, n_samples),
        'Humidity': np.random.uniform(40, 90, n_samples),
        'Thickness': np.random.uniform(10, 200, n_samples)
    }
    
    df = pd.DataFrame(data)
    df.to_csv('semi-processed_2.csv', index=False)
    print(f"✅ Generated semi-processed_2.csv with {n_samples} samples")
    return df

def main():
    """Generate all sample datasets"""
    
    print("\n" + "="*60)
    print("Generating Sample Data for Material Analysis Pipeline")
    print("="*60 + "\n")
    
    generate_rawdata(100)
    generate_golden_transmat(50)
    generate_annotator_files(40)
    generate_perm_data(25)
    generate_semi_processed(100)
    
    print("\n" + "="*60)
    print("✅ All sample data files generated successfully!")
    print("="*60)
    print("\nGenerated files:")
    print("  • rawdata.csv")
    print("  • goldenTRANSMAT-all.csv")
    print("  • goldenTRANSMAT-annotator1.csv")
    print("  • goldenTRANSMAT-annotator2.csv")
    print("  • goldenTRANSMAT-annotator3.csv")
    print("  • 22perm.csv")
    print("  • semi-processed_2.csv")
    print("\nYou can now use these files to test the Streamlit application!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
