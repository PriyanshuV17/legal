"""
ML Model Training for Lawyer Recommendation System
Trains multiple models and selects the best one for inference
"""

import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import os
import json

DATA_DIR = r"D:\legal\models"
PROCESSED_DATA = r"D:\legal\models\lawyers_processed.csv"


def load_processed_data():
    """Load prepared data and artifacts"""
    print("Loading processed data...")
    
    df = pd.read_csv(PROCESSED_DATA)
    
    with open(os.path.join(DATA_DIR, 'label_encoders.pkl'), 'rb') as f:
        encoders = pickle.load(f)
    
    with open(os.path.join(DATA_DIR, 'feature_scaler.pkl'), 'rb') as f:
        scaler = pickle.load(f)
    
    with open(os.path.join(DATA_DIR, 'feature_cols.pkl'), 'rb') as f:
        feature_cols = pickle.load(f)
    
    print(f"Loaded {len(df)} lawyer records")
    return df, encoders, scaler, feature_cols


def train_knn_model(df, feature_cols):
    """Train KNN model for similarity-based recommendations"""
    print("\n" + "="*60)
    print("TRAINING KNN MODEL (Similarity-based)")
    print("="*60)
    
    X = df[feature_cols].values
    
    # Train KNN model
    knn_model = NearestNeighbors(n_neighbors=10, metric='cosine')
    knn_model.fit(X)
    
    print(f"✓ KNN model trained on {len(df)} records")
    print(f"  Features used: {len(feature_cols)}")
    print(f"  Neighbors to find: 10")
    
    return knn_model


def train_ranking_model(df, feature_cols):
    """Train Random Forest for ranking score prediction"""
    print("\n" + "="*60)
    print("TRAINING RANKING MODEL (Random Forest)")
    print("="*60)
    
    X = df[feature_cols[:-1]]  # All except ranking_score
    y = df['ranking_score']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    
    rf_model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = rf_model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"✓ Random Forest model trained")
    print(f"  Train set size: {len(X_train)}")
    print(f"  Test set size: {len(X_test)}")
    print(f"  Mean Squared Error: {mse:.4f}")
    print(f"  R² Score: {r2:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols[:-1],
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n  Top 5 Important Features:")
    for idx, row in feature_importance.head(5).iterrows():
        print(f"    {row['feature']}: {row['importance']:.4f}")
    
    return rf_model, feature_importance


def train_content_based_model(df):
    """Create content-based filtering model metadata"""
    print("\n" + "="*60)
    print("PREPARING CONTENT-BASED MODEL")
    print("="*60)
    
    # Group lawyers by attributes for filtering
    content_model = {
        'by_state': df.groupby('state')['id'].apply(list).to_dict(),
        'by_city': df.groupby('city')['id'].apply(list).to_dict(),
        'by_type': df.groupby('type_of_lawyer')['id'].apply(list).to_dict(),
        'by_court': df.groupby('court_level')['id'].apply(list).to_dict(),
        'by_language': df.groupby('language')['id'].apply(list).to_dict(),
        'all_lawyers': df[['id', 'name', 'type_of_lawyer', 'state', 'city', 
                           'language', 'court_level', 'ranking_score', 'rating']].to_dict('records')
    }
    
    print(f"✓ Content-based model created")
    print(f"  States: {len(content_model['by_state'])}")
    print(f"  Cities: {len(content_model['by_city'])}")
    print(f"  Lawyer Types: {len(content_model['by_type'])}")
    print(f"  Court Levels: {len(content_model['by_court'])}")
    print(f"  Languages: {len(content_model['by_language'])}")
    
    return content_model


def save_models(knn_model, rf_model, content_model, feature_importance):
    """Save all trained models"""
    print("\n" + "="*60)
    print("SAVING MODELS")
    print("="*60)
    
    # Save KNN model
    with open(os.path.join(DATA_DIR, 'knn_model.pkl'), 'wb') as f:
        pickle.dump(knn_model, f)
    print("✓ Saved: knn_model.pkl")
    
    # Save Random Forest model
    with open(os.path.join(DATA_DIR, 'ranking_model.pkl'), 'wb') as f:
        pickle.dump(rf_model, f)
    print("✓ Saved: ranking_model.pkl")
    
    # Save content-based model
    with open(os.path.join(DATA_DIR, 'content_model.pkl'), 'wb') as f:
        pickle.dump(content_model, f)
    print("✓ Saved: content_model.pkl")
    
    # Save feature importance
    feature_importance.to_csv(os.path.join(DATA_DIR, 'feature_importance.csv'), index=False)
    print("✓ Saved: feature_importance.csv")
    
    # Save metadata
    metadata = {
        'model_type': 'ensemble_recommendation',
        'version': '1.0',
        'models': ['knn_similarity', 'random_forest_ranking', 'content_based_filtering'],
        'data_samples': len(df),
        'status': 'ready'
    }
    
    with open(os.path.join(DATA_DIR, 'model_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    print("✓ Saved: model_metadata.json")


def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "   LEGAL SYSTEM - LAWYER RECOMMENDATION MODEL TRAINING  ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Load data
    df, encoders, scaler, feature_cols = load_processed_data()
    
    # Train models
    knn_model = train_knn_model(df, feature_cols)
    rf_model, feature_importance = train_ranking_model(df, feature_cols)
    content_model = train_content_based_model(df)
    
    # Save models
    save_models(knn_model, rf_model, content_model, feature_importance, df)
    
    print("\n" + "="*60)
    print("✓✓✓ MODEL TRAINING COMPLETE ✓✓✓")
    print("="*60)
    print("\nModels ready for inference!")
    print("Location:", DATA_DIR)
    print("\nNext step: Update backend with inference endpoint")
    print("=" * 60)


if __name__ == "__main__":
    main()
