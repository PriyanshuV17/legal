"""
Data preparation script for lawyer recommendation system
Handles feature engineering and data preprocessing
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import os

DATA_PATH = r"D:\legal\data\lawyers_large.csv'.csv"
OUTPUT_DIR = r"D:\legal\models"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_and_prepare_data():
    """Load lawyers data and perform feature engineering"""
    print("Loading lawyers data...")
    df = pd.read_csv(DATA_PATH)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Handle missing values
    df = df.fillna(df.mean(numeric_only=True))
    df['language'] = df['language'].fillna('Hindi/English')
    df['availability'] = df['availability'].fillna('Available')
    
    # Create ranking score (0-100)
    df['ranking_score'] = (
        (df['rating'] / 5 * 40) +  # 40% rating
        (df['cases_won'] / df['cases_fought'] * 30) +  # 30% win rate
        (df['experience_years'] / df['experience_years'].max() * 20) +  # 20% experience
        (df['cases_fought'] / df['cases_fought'].max() * 10)  # 10% cases handled
    ).round(2)
    
    print(f"\nRanking Score Stats:")
    print(df['ranking_score'].describe())
    
    return df


def engineer_features(df):
    """Create features for ML model"""
    print("\nEngineering features...")
    
    # Encode categorical variables
    encoders = {}
    categorical_cols = ['type_of_lawyer', 'state', 'city', 'language', 'court_level', 'availability']
    
    for col in categorical_cols:
        le = LabelEncoder()
        df[f'{col}_encoded'] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
    
    # Extract numeric features from fee_range (e.g., "3793-75050" -> min and max)
    fee_splits = df['fee_range'].str.split('-', expand=True).astype(float)
    df['fee_min'] = fee_splits[0]
    df['fee_max'] = fee_splits[1]
    df['fee_avg'] = (df['fee_min'] + df['fee_max']) / 2
    
    # Win rate
    df['win_rate'] = (df['cases_won'] / df['cases_fought']).fillna(0)
    
    # Availability score
    df['availability_score'] = df['availability'].apply(
        lambda x: 1 if x == 'Available' else 0.5
    )
    
    # Online consultation availability score
    df['online_score'] = df['online_consultation'].apply(
        lambda x: 0.5 if x == 'Yes' else 0
    )
    
    print(f"Feature engineering complete. New columns created:")
    print([col for col in df.columns if col.endswith('_encoded')])
    
    return df, encoders


def create_feature_matrix(df):
    """Create feature matrix for ML model"""
    print("\nCreating feature matrix...")
    
    feature_cols = [
        'type_of_lawyer_encoded', 'court_level_encoded', 'state_encoded', 
        'city_encoded', 'language_encoded',
        'experience_years', 'cases_fought', 'win_rate', 'fee_avg',
        'availability_score', 'online_score', 'ranking_score'
    ]
    
    X = df[feature_cols].copy()
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)
    
    return X_scaled, scaler, feature_cols


def save_artifacts(df, encoders, scaler, feature_cols):
    """Save processed data and transformers"""
    print(f"\nSaving artifacts to {OUTPUT_DIR}...")
    
    # Save processed dataframe
    df.to_csv(os.path.join(OUTPUT_DIR, 'lawyers_processed.csv'), index=False)
    
    # Save encoders
    with open(os.path.join(OUTPUT_DIR, 'label_encoders.pkl'), 'wb') as f:
        pickle.dump(encoders, f)
    
    # Save scaler
    with open(os.path.join(OUTPUT_DIR, 'feature_scaler.pkl'), 'wb') as f:
        pickle.dump(scaler, f)
    
    # Save feature columns info
    with open(os.path.join(OUTPUT_DIR, 'feature_cols.pkl'), 'wb') as f:
        pickle.dump(feature_cols, f)
    
    print("✓ Saved: lawyers_processed.csv")
    print("✓ Saved: label_encoders.pkl")
    print("✓ Saved: feature_scaler.pkl")
    print("✓ Saved: feature_cols.pkl")
    
    print(f"\nDataset Summary:")
    print(f"Total Lawyers: {len(df)}")
    print(f"States: {df['state'].nunique()}")
    print(f"Cities: {df['city'].nunique()}")
    print(f"Lawyer Types: {df['type_of_lawyer'].nunique()}")
    print(f"Languages: {df['language'].nunique()}")


def main():
    print("=" * 60)
    print("LEGAL SYSTEM - LAWYER DATA PREPARATION")
    print("=" * 60)
    
    # Load and prepare
    df = load_and_prepare_data()
    
    # Engineer features
    df, encoders = engineer_features(df)
    
    # Create feature matrix
    X_scaled, scaler, feature_cols = create_feature_matrix(df)
    
    # Save all artifacts
    save_artifacts(df, encoders, scaler, feature_cols)
    
    print("\n" + "=" * 60)
    print("✓ DATA PREPARATION COMPLETE")
    print("=" * 60)
    print(f"\nNext step: Run train_lawyer_model.py to train the recommendation system")


if __name__ == "__main__":
    main()
