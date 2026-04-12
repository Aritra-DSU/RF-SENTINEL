import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# ✅ Load labeled dataset
df = pd.read_csv("labeled_data.csv")

# ✅ Check columns (debug safety)
print("Columns:", df.columns)

# ✅ Select features (keep it simple & stable)
X = df[["norm_freq", "Signal Strength"]]

# ✅ Target label
y = df["label"]

# ✅ Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ✅ Create model (strong + fast)
model = RandomForestClassifier(n_estimators=200, random_state=42)

# ✅ Train model
model.fit(X_train, y_train)

# ✅ Accuracy check
accuracy = model.score(X_test, y_test)
print(f"✅ Model Accuracy: {accuracy * 100:.2f}%")

# ✅ Save model
joblib.dump(model, "model.pkl")

print("✅ Model saved as model.pkl")