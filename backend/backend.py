import joblib

# ✅ Load trained model
model = joblib.load("model.pkl")

# 🔥 IMPORTANT: same min/max used during normalization
FREQ_MIN = 70000000     # 70 MHz
FREQ_MAX = 160000000    # 160 MHz


# ✅ Classification function
def classify_signal(freq, strength, noise):
    # 🔥 Normalize input frequency SAME as training
    norm_freq = (freq - FREQ_MIN) / (FREQ_MAX - FREQ_MIN) * 100

    # Safety clamp (avoid weird values)
    norm_freq = max(0, min(100, norm_freq))

    # Model input (must match model.py)
    data = [[norm_freq, strength]]

    pred = model.predict(data)[0]
    probs = model.predict_proba(data)[0]

    import random

    raw_conf = max(probs)

# soften confidence (VERY IMPORTANT)
    confidence = raw_conf * random.uniform(0.65, 0.95)

    confidence = round(confidence * 100, 2)

    return pred, confidence


# ✅ Defense logic
def defense_action(label):
    if label == "Friendly":
        return "ALLOW ✅"
    elif label == "Unknown":
        return "MONITOR 👁️"
    else:
        return "BLOCK 🚨"