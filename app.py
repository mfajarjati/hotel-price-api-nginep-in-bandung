from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
from datetime import datetime, timedelta
import math
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize model variable
model = None

# Load model on startup if exists
model_path = os.path.join(os.path.dirname(__file__), 'models', 'hotel_price_model.pkl')
try:
    if os.path.exists(model_path):
        print(f"Loading model from {model_path}")
        model = joblib.load(model_path)
        print("Model loaded successfully")
    else:
        print(f"Model not found at {model_path}, will use fallback logic")
except Exception as e:
    print(f"Error loading model: {e}")

@app.route('/', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "ok", 
        "message": "Hotel price prediction API is running",
        "model_loaded": model is not None
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Predict hotel prices based on input data"""
    try:
        data = request.json
        
        # Extract features
        hotel_id = data.get('hotelId', '')
        rating = float(data.get('rating', 0))
        reviews_count = int(data.get('reviewsCount', 0))
        avg_distance = float(data.get('avgDistance', 1.0))
        amenities_count = int(data.get('amenitiesCount', 5))
        check_in_date = data.get('checkInDate', datetime.now().strftime('%Y-%m-%d'))
        
        # If model is loaded, use it for prediction
        if model is not None:
            features = np.array([[
                rating, 
                reviews_count, 
                avg_distance, 
                amenities_count
            ]])
            base_price = int(model.predict(features)[0])
            print(f"Model prediction: {base_price}")
        else:
            # Fallback to rule-based pricing model
            print("Using rule-based pricing model")
            base_price = calculate_rule_based_price(
                rating, reviews_count, avg_distance, amenities_count, check_in_date
            )
            
        # Generate predictions for 60 days
        predictions = generate_daily_predictions(hotel_id, base_price, check_in_date)
        
        return jsonify({
            "success": True,
            "basePrice": base_price,
            "predictions": predictions
        })
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def calculate_rule_based_price(rating, reviews_count, avg_distance, amenities_count, check_in_date):
    """Calculate base price using rule-based approach"""
    base_price = 500000  # Default starting point
    
    # Apply rating factor (higher rating = higher price)
    rating_factor = math.pow(rating / 5, 1.5) * 1.5 if rating else 1
    
    # Apply review count factor (more reviews = more popular = higher price)
    reviews_factor = min(1 + math.log(max(reviews_count, 1)) / 20, 1.3)
    
    # Apply amenities factor
    amenities_factor = 1 + amenities_count / 20
    
    # Apply location factor (closer to attractions = higher price)
    distance_factor = max(0.8, 1 - avg_distance / 10)
    
    # Get date information
    check_in = datetime.strptime(check_in_date, '%Y-%m-%d')
    day_of_week = check_in.weekday()
    month = check_in.month - 1
    is_weekend = day_of_week >= 4  # Friday, Saturday, Sunday
    
    weekend_factor = 1.15 if is_weekend else 1
    
    # Seasonal factor (high season = higher prices)
    # Holiday months: June-July, December-January
    seasonal_factor = 1.2 if (month >= 5 and month <= 6) or month >= 11 or month == 0 else 0.9 if (month >= 8 and month <= 10) else 1
    
    # Calculate the final price
    predicted_price = round(
        base_price * rating_factor * reviews_factor * amenities_factor * 
        distance_factor * weekend_factor * seasonal_factor
    )
    
    return predicted_price

def generate_daily_predictions(hotel_id, base_price, start_date):
    """Generate price predictions for 60 days from start date"""
    predictions = []
    today = datetime.strptime(start_date, '%Y-%m-%d')
    
    # Create a deterministic seed based on hotelId
    seed = sum(ord(c) for c in hotel_id) if hotel_id else 42
    
    for i in range(60):
        date = today + timedelta(days=i)
        
        # Factor in day of week (weekends cost more)
        day_of_week = date.weekday()
        is_weekend = day_of_week >= 4  # Friday, Saturday, Sunday
        weekend_multiplier = 1.15 if is_weekend else 1
        
        # Factor in seasonality
        month = date.month - 1  # 0-indexed month
        seasonal_factor = 1.2 if (month >= 5 and month <= 6) or month >= 11 or month == 0 else 0.9 if (month >= 8 and month <= 10) else 1
        
        # Add some randomness but keep it deterministic for the same hotel
        random_factor = 0.95 + ((math.sin((seed + i) * 0.1) * 10000) % 1) * 0.1
        
        # Calculate the price for this day
        price = round(base_price * weekend_multiplier * seasonal_factor * random_factor)
        
        predictions.append({
            "date": date.strftime('%Y-%m-%d'),
            "price": price
        })
    
    return predictions

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)