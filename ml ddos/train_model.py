import pandas as pd
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import pickle

data = []
for _ in range(1000):
    packet_count = random.randint(20, 100) 
    unique_ips = random.randint(1, 5)
    attack = 1 if packet_count > 70 else 0  
    data.append([packet_count, unique_ips, attack])

df = pd.DataFrame(data, columns=["packet_count", "unique_ips", "attack"])

X = df[["packet_count", "unique_ips"]]
y = df["attack"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
model = RandomForestClassifier()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

with open("ddos_model.pkl", "wb") as f:
    pickle.dump(model, f)
