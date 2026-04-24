import joblib

model = joblib.load("model.pkl")


FREQ_MIN = 70000000    
FREQ_MAX = 160000000    


def classify_signal(freq, strength, noise):
   
    norm_freq = (freq - FREQ_MIN) / (FREQ_MAX - FREQ_MIN) * 100

   
    norm_freq = max(0, min(100, norm_freq))

   
    data = [[norm_freq, strength]]

    pred = model.predict(data)[0]
    probs = model.predict_proba(data)[0]

    import random

    raw_conf = max(probs)


    confidence = raw_conf * random.uniform(0.65, 0.95)

    confidence = round(confidence * 100, 2)

    return pred, confidence



def defense_action(label):
    if label == "Friendly":
        return "ALLOW ✅"
    elif label == "Unknown":
        return "MONITOR 👁️"
    else:
        return "BLOCK 🚨"
