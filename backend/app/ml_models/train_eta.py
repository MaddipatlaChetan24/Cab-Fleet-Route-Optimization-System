import random
import joblib
import os
from sklearn.linear_model import LinearRegression

X = []
y = []

# Synthetic training data
for _ in range(5000):
    dist = random.uniform(0.5, 25)
    traffic = random.uniform(1.0, 1.5)

    speed = 30 / traffic
    eta = (dist / speed) * 60

    X.append([dist, traffic])
    y.append(eta)

model = LinearRegression()
model.fit(X, y)

os.makedirs("backend/app/ml_models", exist_ok=True)
joblib.dump(model, "backend/app/ml_models/eta_model.pkl")

print("ETA MODEL TRAINED")