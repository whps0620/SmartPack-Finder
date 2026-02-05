"""
Configuration file for Material Analysis Pipeline
Modify these settings to customize the application behavior
"""

# Application Settings
APP_CONFIG = {
    'title': 'Material Analysis Pipeline',
    'icon': '🔬',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Data Processing Settings
DATA_CONFIG = {
    'max_file_size_mb': 200,  # Maximum file upload size in MB
    'chunk_size': 10000,  # Process data in chunks for large files
    'missing_value_threshold': 0.5,  # Drop columns with >50% missing values
    'categorical_threshold': 10  # Max unique values to treat as categorical
}

# NLP Settings
NLP_CONFIG = {
    'spacy_model': 'en_core_web_sm',
    'max_keywords': 10,  # Maximum keywords to extract
    'tfidf_max_features': 100,
    'stop_words': 'english',
    'min_keyword_length': 3
}

# Model Training Settings
MODEL_CONFIG = {
    'test_size': 0.2,
    'random_state': 42,
    'cv_folds': 5,  # Cross-validation folds
    'n_jobs': -1  # Use all CPU cores
}

# Random Forest Settings
RF_CONFIG = {
    'n_estimators': 100,
    'max_depth': None,
    'min_samples_split': 2,
    'min_samples_leaf': 1,
    'random_state': 42
}

# Gradient Boosting Settings
GB_CONFIG = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': 3,
    'random_state': 42
}

# XGBoost Settings
XGB_CONFIG = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': 3,
    'random_state': 42,
    'tree_method': 'auto'
}

# SVM Settings
SVM_CONFIG = {
    'kernel': 'rbf',
    'C': 1.0,
    'gamma': 'scale',
    'random_state': 42
}

# KNN Settings
KNN_CONFIG = {
    'n_neighbors': 5,
    'weights': 'uniform',
    'algorithm': 'auto'
}

# Logistic Regression Settings
LR_CONFIG = {
    'max_iter': 1000,
    'random_state': 42,
    'solver': 'lbfgs',
    'multi_class': 'auto'
}

# Decision Tree Settings
DT_CONFIG = {
    'max_depth': None,
    'min_samples_split': 2,
    'min_samples_leaf': 1,
    'random_state': 42
}

# Visualization Settings
VIZ_CONFIG = {
    'default_figsize': (10, 6),
    'heatmap_cmap': 'YlGnBu',
    'bar_color': 'steelblue',
    'confusion_matrix_cmap': 'Blues',
    'font_size': 12,
    'title_font_size': 14,
    'dpi': 100
}

# Color Schemes
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#2ca02c',
    'accent': '#ff7f0e',
    'error': '#d62728',
    'success': '#2ca02c',
    'warning': '#ff7f0e',
    'info': '#17a2b8'
}

# File Paths (for default data location)
PATHS = {
    'data_dir': 'data/',
    'output_dir': 'output/',
    'models_dir': 'models/',
    'logs_dir': 'logs/'
}

# Feature Engineering Settings
FEATURE_CONFIG = {
    'scaling_method': 'standard',  # 'standard', 'minmax', 'robust'
    'encoding_method': 'label',  # 'label', 'onehot'
    'handle_missing': 'drop',  # 'drop', 'mean', 'median', 'mode'
    'outlier_method': 'iqr'  # 'iqr', 'zscore', 'none'
}

# Performance Metrics
METRICS_CONFIG = {
    'primary_metric': 'accuracy',
    'secondary_metrics': ['precision', 'recall', 'f1'],
    'average_method': 'weighted'  # For multi-class problems
}

# Advanced Settings
ADVANCED_CONFIG = {
    'enable_caching': True,
    'debug_mode': False,
    'show_warnings': True,
    'auto_reload': False,
    'enable_profiling': False
}

# Export Settings
EXPORT_CONFIG = {
    'default_format': 'csv',
    'include_index': False,
    'date_format': '%Y-%m-%d',
    'float_format': '%.3f'
}

# Text Processing
TEXT_CONFIG = {
    'max_text_length': 1000,
    'remove_punctuation': False,
    'lowercase': True,
    'remove_numbers': False
}

# Material-Specific Settings
MATERIAL_CONFIG = {
    'base_materials': [
        'PLA', 'LDPE', 'HDPE', 'PP', 'PET', 
        'chitosan', 'gelatin', 'starch', 
        'methylcellulose', 'corn zein'
    ],
    'material_types': [
        'individual', 'coated', 'nanocomposite', 
        'composite', 'blend'
    ],
    'common_secondary_materials': [
        'montmorillonite', 'clay', 'nanoclay', 
        'silica', 'cellulose'
    ],
    'target_properties': [
        'OP', 'OTR', 'WVP', 'WVTR', 'PCO2'
    ]
}

# UI Customization
UI_CONFIG = {
    'show_dataframe_height': 400,
    'max_rows_display': 100,
    'show_progress_bar': True,
    'enable_tooltips': True,
    'compact_mode': False
}

# Logging Settings
LOG_CONFIG = {
    'level': 'INFO',  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'save_logs': False,
    'log_file': 'app.log'
}

def get_all_configs():
    """Return all configuration dictionaries"""
    return {
        'app': APP_CONFIG,
        'data': DATA_CONFIG,
        'nlp': NLP_CONFIG,
        'model': MODEL_CONFIG,
        'rf': RF_CONFIG,
        'gb': GB_CONFIG,
        'xgb': XGB_CONFIG,
        'svm': SVM_CONFIG,
        'knn': KNN_CONFIG,
        'lr': LR_CONFIG,
        'dt': DT_CONFIG,
        'viz': VIZ_CONFIG,
        'colors': COLORS,
        'paths': PATHS,
        'features': FEATURE_CONFIG,
        'metrics': METRICS_CONFIG,
        'advanced': ADVANCED_CONFIG,
        'export': EXPORT_CONFIG,
        'text': TEXT_CONFIG,
        'material': MATERIAL_CONFIG,
        'ui': UI_CONFIG,
        'log': LOG_CONFIG
    }

def print_config_summary():
    """Print a summary of current configuration"""
    print("\n" + "="*60)
    print("Material Analysis Pipeline - Configuration Summary")
    print("="*60 + "\n")
    
    configs = get_all_configs()
    
    for section, config in configs.items():
        print(f"\n{section.upper()} Configuration:")
        print("-" * 40)
        for key, value in config.items():
            print(f"  {key}: {value}")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    print_config_summary()
