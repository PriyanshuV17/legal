"""
Lawyer Recommendation Inference Module
Real-time lawyer recommendations using trained models
"""

import pandas as pd
import numpy as np
import pickle
import os
from typing import List, Dict, Any

MODEL_DIR = r"D:\legal\models"


class LawyerRecommender:
    """Main recommendation engine"""
    
    def __init__(self):
        self.load_models()
        self.df = pd.read_csv(os.path.join(MODEL_DIR, 'lawyers_processed.csv'))
        
    def load_models(self):
        """Load all trained models"""
        print("Loading lawyer recommendation models...")
        
        with open(os.path.join(MODEL_DIR, 'knn_model.pkl'), 'rb') as f:
            self.knn_model = pickle.load(f)
        
        with open(os.path.join(MODEL_DIR, 'ranking_model.pkl'), 'rb') as f:
            self.rf_model = pickle.load(f)
        
        with open(os.path.join(MODEL_DIR, 'content_model.pkl'), 'rb') as f:
            self.content_model = pickle.load(f)
        
        with open(os.path.join(MODEL_DIR, 'label_encoders.pkl'), 'rb') as f:
            self.encoders = pickle.load(f)
        
        with open(os.path.join(MODEL_DIR, 'feature_scaler.pkl'), 'rb') as f:
            self.scaler = pickle.load(f)
        
        with open(os.path.join(MODEL_DIR, 'feature_cols.pkl'), 'rb') as f:
            self.feature_cols = pickle.load(f)
        
        print("✓ Models loaded successfully")
    
    def recommend_by_filters(
        self,
        case_type: str = None,
        state: str = None,
        city: str = None,
        language: str = None,
        court_level: str = None,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get lawyer recommendations based on filters and ranking
        
        Args:
            case_type: Type of lawyer (Criminal, Civil, etc.)
            state: State preference
            city: City preference
            language: Preferred language
            court_level: Court level (District, High, Supreme)
            top_n: Number of recommendations
            
        Returns:
            List of recommended lawyers with scores
        """
        
        results = self.content_model['all_lawyers'].copy()
        
        # Apply filters
        if case_type:
            results = [l for l in results if l['type_of_lawyer'].lower() == case_type.lower()]
        
        if state:
            results = [l for l in results if l['state'].lower() == state.lower()]
        
        if city:
            results = [l for l in results if l['city'].lower() == city.lower()]
        
        if language:
            results = [l for l in results if language.lower() in l['language'].lower()]
        
        if court_level:
            results = [l for l in results if l['court_level'].lower() == court_level.lower()]
        
        # Sort by ranking score (already computed)
        results = sorted(results, key=lambda x: x['ranking_score'], reverse=True)
        
        return results[:top_n]
    
    def get_similar_lawyers(
        self,
        lawyer_id: int,
        top_n: int = 5,
        exclude_self: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find lawyers similar to a given lawyer
        
        Args:
            lawyer_id: ID of reference lawyer
            top_n: Number of similar lawyers to return
            exclude_self: Whether to exclude the reference lawyer
            
        Returns:
            List of similar lawyers
        """
        
        # Get lawyer index
        lawyer_idx = self.df[self.df['id'] == lawyer_id].index[0]
        
        # Get feature vector
        X = self.df[self.feature_cols].values
        lawyer_vector = X[lawyer_idx:lawyer_idx+1]
        
        # Find similar lawyers
        distances, indices = self.knn_model.kneighbors(lawyer_vector)
        
        # Get results
        results = []
        n_neighbors = top_n + 1 if exclude_self else top_n
        
        for idx, distance in zip(indices[0][:n_neighbors], distances[0][:n_neighbors]):
            if exclude_self and idx == lawyer_idx:
                continue
            
            lawyer = self.df.iloc[idx]
            results.append({
                'id': int(lawyer['id']),
                'name': lawyer['name'],
                'type_of_lawyer': lawyer['type_of_lawyer'],
                'state': lawyer['state'],
                'city': lawyer['city'],
                'language': lawyer['language'],
                'court_level': lawyer['court_level'],
                'ranking_score': float(lawyer['ranking_score']),
                'rating': float(lawyer['rating']),
                'similarity_score': float(1 - distance)
            })
            
            if len(results) == top_n:
                break
        
        return results
    
    def get_top_lawyers_by_location(
        self,
        state: str,
        city: str = None,
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top-rated lawyers in a specific location"""
        
        lawyers = self.df[self.df['state'] == state]
        
        if city:
            lawyers = lawyers[lawyers['city'] == city]
        
        lawyers = lawyers.sort_values('ranking_score', ascending=False).head(top_n)
        
        return [
            {
                'id': int(row['id']),
                'name': row['name'],
                'type_of_lawyer': row['type_of_lawyer'],
                'state': row['state'],
                'city': row['city'],
                'language': row['language'],
                'court_level': row['court_level'],
                'ranking_score': float(row['ranking_score']),
                'rating': float(row['rating']),
                'experience_years': int(row['experience_years']),
                'cases_fought': int(row['cases_fought']),
                'win_rate': float(row['win_rate'])
            }
            for _, row in lawyers.iterrows()
        ]
    
    def get_lawyer_details(self, lawyer_id: int) -> Dict[str, Any]:
        """Get complete details of a lawyer"""
        
        lawyer = self.df[self.df['id'] == lawyer_id]
        
        if lawyer.empty:
            return None
        
        lawyer = lawyer.iloc[0]
        
        return {
            'id': int(lawyer['id']),
            'name': lawyer['name'],
            'gender': lawyer['gender'],
            'type_of_lawyer': lawyer['type_of_lawyer'],
            'specialization': lawyer['specialization'],
            'court_level': lawyer['court_level'],
            'state': lawyer['state'],
            'city': lawyer['city'],
            'email': lawyer['email'],
            'mobile': lawyer['mobile'],
            'cases_fought': int(lawyer['cases_fought']),
            'cases_won': int(lawyer['cases_won']),
            'cases_lost': int(lawyer['cases_lost']),
            'experience_years': int(lawyer['experience_years']),
            'fee_range': lawyer['fee_range'],
            'language': lawyer['language'],
            'availability': lawyer['availability'],
            'online_consultation': lawyer['online_consultation'],
            'rating': float(lawyer['rating']),
            'ranking_score': float(lawyer['ranking_score']),
            'win_rate': float(lawyer['win_rate'])
        }
    
    def search_lawyers(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search lawyers by name or city with optional filters
        
        Args:
            query: Search query (name or city)
            filters: Additional filters (type, state, language, etc.)
            top_n: Number of results
            
        Returns:
            List of matching lawyers
        """
        
        results = self.df.copy()
        
        # Text search
        query_lower = query.lower()
        results = results[
            (results['name'].str.lower().str.contains(query_lower, na=False)) |
            (results['city'].str.lower().str.contains(query_lower, na=False))
        ]
        
        # Apply filters if provided
        if filters:
            if 'type_of_lawyer' in filters:
                results = results[results['type_of_lawyer'] == filters['type_of_lawyer']]
            
            if 'state' in filters:
                results = results[results['state'] == filters['state']]
            
            if 'language' in filters:
                lang = filters['language'].lower()
                results = results[results['language'].str.lower().str.contains(lang, na=False)]
            
            if 'min_rating' in filters:
                results = results[results['rating'] >= filters['min_rating']]
            
            if 'court_level' in filters:
                results = results[results['court_level'] == filters['court_level']]
        
        # Sort by ranking score
        results = results.sort_values('ranking_score', ascending=False).head(top_n)
        
        return [
            {
                'id': int(row['id']),
                'name': row['name'],
                'type_of_lawyer': row['type_of_lawyer'],
                'state': row['state'],
                'city': row['city'],
                'language': row['language'],
                'court_level': row['court_level'],
                'ranking_score': float(row['ranking_score']),
                'rating': float(row['rating']),
                'mobile': row['mobile'],
                'email': row['email']
            }
            for _, row in results.iterrows()
        ]


# Initialize global recommender instance
_recommender = None

def get_recommender():
    """Get or create recommender instance"""
    global _recommender
    if _recommender is None:
        _recommender = LawyerRecommender()
    return _recommender


# Test the module
if __name__ == "__main__":
    print("Testing Lawyer Recommendation System...\n")
    
    recommender = get_recommender()
    
    # Test 1: Filter-based recommendation
    print("Test 1: Get Criminal Lawyers in Bihar, Patna")
    results = recommender.recommend_by_filters(
        case_type="Criminal",
        state="Bihar",
        city="Patna",
        top_n=5
    )
    for lawyer in results:
        print(f"  {lawyer['name']} - {lawyer['ranking_score']:.2f}")
    
    # Test 2: Get top lawyers by location
    print("\nTest 2: Top Lawyers in Delhi")
    results = recommender.get_top_lawyers_by_location("Delhi", top_n=3)
    for lawyer in results:
        print(f"  {lawyer['name']} - Rating: {lawyer['rating']}, Score: {lawyer['ranking_score']:.2f}")
    
    print("\n✓ Recommendation system is working!")
