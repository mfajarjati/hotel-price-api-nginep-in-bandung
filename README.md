---
title: Hotel Price API for Nginep in Bandung
emoji: 🏨
colorFrom: yellow
colorTo: brown
sdk: docker
pinned: false
---

# Hotel Price Prediction API

This API predicts hotel prices based on features like rating, reviews, distance, and amenities.

## Endpoints

### Health Check

- `GET /`
- Returns the status of the API and whether the model is loaded

### Predict Price

- `POST /predict`
- Input: JSON with hotel features
- Returns: Base price prediction and daily price forecasts

## Example Usage

```python
import requests

response = requests.post(
    "https://mfajarjati-hotel-price-api-nginep-in-bandung.hf.space/predict",
    json={
        "hotelId": "hotel123",
        "rating": 4.5,
        "reviewsCount": 120,
        "avgDistance": 1.2,
        "amenitiesCount": 8,
        "checkInDate": "2025-04-10"
    }
)

print(response.json())
```
