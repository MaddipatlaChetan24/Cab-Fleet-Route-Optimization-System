import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

# Create directory if not exists
SAVE_PATH = os.path.dirname(__file__)

def generate_synthetic_data(days=100):
    data = []
    start_date = datetime(2025, 1, 1)
    
    for i in range(days * 24):
        current_time = start_date + timedelta(hours=i)
        hour = current_time.hour
        day_of_week = current_time.weekday()
        
        # Base demand: Higher on weekdays, peaks at 8AM and 5PM
        base_demand = 100
        if day_of_week < 5: # Weekday
            if hour == 8 or hour == 17:
                base_demand = 200 + np.random.randint(20, 50)
            elif 9 <= hour <= 16:
                base_demand = 120 + np.random.randint(10, 30)
        else: # Weekend
            base_demand = 50 + np.random.randint(0, 20)
            
        # Add some noise
        demand = base_demand + np.random.randint(-10, 10)
        
        data.append({
            'hour': hour,
            'day_of_week': day_of_week,
            'demand': max(0, demand)
        })
        
    return pd.DataFrame(data)

def train_and_save():
    df = generate_synthetic_data()
    X = df[['hour', 'day_of_week']]
    y = df['demand']
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    import pickle
    with open(os.path.join(SAVE_PATH, 'demand_model.pkl'), 'wb') as f:
        pickle.dump(model, f)
        
    print(f"Model trained and saved to {os.path.join(SAVE_PATH, 'demand_model.pkl')}")

if __name__ == "__main__":
    train_and_save()
