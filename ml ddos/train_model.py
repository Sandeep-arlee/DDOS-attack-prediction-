import pandas as pd
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

# Generate synthetic traffic data
data = []
for _ in range(1000):
    packet_count = random.randint(20, 100)  # Random number of packets
    unique_ips = random.randint(1, 5)  # Random number of unique IPs
    attack = 1 if packet_count > 70 else 0  # If packet count is high, it's an attack
    data.append([packet_count, unique_ips, attack])

# Create a DataFrame
df = pd.DataFrame(data, columns=["packet_count", "unique_ips", "attack"])

# Split the data into features and target
X = df[["packet_count", "unique_ips"]]
y = df["attack"]

# Train a RandomForestClassifier
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# Save the model
with open("ddos_model.pkl", "wb") as f:
    pickle.dump(model, f)
