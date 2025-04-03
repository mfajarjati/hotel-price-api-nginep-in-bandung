import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import os

def create_dummy_model():
    """Create a simple model that approximates hotel price predictions"""
    print("Creating dummy Random Forest model...")
    
    # Create a dummy dataset that simulates hotel features
    X = np.array([
        # rating, reviews, distance, amenities
        [4.5, 1000, 0.5, 15],  # Luxury close hotel
        [4.8, 2000, 0.2, 20],  # Premium luxury hotel
        [3.5, 500, 1.5, 8],    # Mid-range hotel
        [3.0, 200, 2.5, 5],    # Budget hotel
        [2.5, 100, 3.5, 3],    # Economy hotel
    ])
    
    # Target prices (in IDR)
    y = np.array([1200000, 1800000, 800000, 600000, 450000])
    
    # Create and train the model
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Save the model
    model_path = 'models/hotel_price_model.pkl'
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    
    # Test the model
    test_prediction = model.predict([[4.2, 800, 1.0, 12]])
    print(f"Test prediction for a 4.2-star hotel with 800 reviews, 1.0km distance, and 12 amenities: {test_prediction[0]} IDR")

if __name__ == "__main__":
    create_dummy_model()