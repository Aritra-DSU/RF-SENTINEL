import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

df = pd.read_csv("labeled_data.csv")


print("Columns:", df.columns)


X = df[["norm_freq", "Signal Strength"]]


y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


model = RandomForestClassifier(n_estimators=200, random_state=42)


model.fit(X_train, y_train)


accuracy = model.score(X_test, y_test)
print(f"✅ Model Accuracy: {accuracy * 100:.2f}%")

# ✅ Save model
joblib.dump(model, "model.pkl")

print("✅ Model saved as model.pkl")
