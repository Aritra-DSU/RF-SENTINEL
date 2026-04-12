# ⬡ RF SENTINEL — API Documentation

> Internal API reference for RF Sentinel's backend inference engine (`backend.py`).  
> These functions form the core classification and defense layer consumed by the Streamlit dashboard.

---

## Overview

The RF Sentinel backend exposes two primary functions:

| Function | Description |
|----------|-------------|
| `classify_signal(freq, strength, noise)` | Classifies an RF signal using the trained ML model |
| `defense_action(label)` | Returns the recommended defense response for a given classification |

---

## Constants

```python
FREQ_MIN = 70_000_000    # 70 MHz — lower bound of the operational spectrum
FREQ_MAX = 160_000_000   # 160 MHz — upper bound of the operational spectrum
```

These constants define the normalization range used during both **model training** and **inference**. They must remain consistent across `prepare_data.py`, `model.py`, and `backend.py` — changing them without retraining will produce incorrect classifications.

---

## Functions

---

### `classify_signal(freq, strength, noise)`

Normalizes the incoming signal parameters and runs inference using the pre-trained Random Forest model.

#### Parameters

| Name | Type | Unit | Range | Description |
|------|------|------|-------|-------------|
| `freq` | `float` | Hz | 70,000,000 – 160,000,000 | Raw signal frequency in Hertz |
| `strength` | `float` | — | 0.0 – 1.0 | Normalized signal strength (0 = weakest, 1 = strongest) |
| `noise` | `float` | — | 0.0 – 0.5 | Noise floor level (accepted but not used as a model feature) |

> **Note:** `noise` is accepted as a parameter for interface consistency with the dashboard but is not passed to the model. Only `norm_freq` and `strength` are used as features — matching the training schema in `model.py`.

#### Returns

| Value | Type | Description |
|-------|------|-------------|
| `label` | `str` | Classification result — `"Friendly"`, `"Unknown"`, or `"Hostile"` |
| `confidence` | `float` | Model confidence as a percentage (0.00 – 100.00) |

#### Example

```python
from backend import classify_signal

label, confidence = classify_signal(
    freq=145_000_000,   # 145 MHz (MILITARY band)
    strength=0.85,
    noise=0.1
)

print(label)       # "Hostile"
print(confidence)  # 94.5
```

#### Internals

```
1. norm_freq = (freq - FREQ_MIN) / (FREQ_MAX - FREQ_MIN) * 100
2. norm_freq  clamped to [0, 100]
3. model.predict([[norm_freq, strength]])       → label
4. model.predict_proba([[norm_freq, strength]]) → confidence
```

---

### `defense_action(label)`

Maps a classification label to a recommended defense response string.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| `label` | `str` | Classification label returned by `classify_signal()` |

#### Returns

| Value | Type | Description |
|-------|------|-------------|
| `action` | `str` | Defense directive string |

#### Response Map

| Label | Action | Meaning |
|-------|--------|---------|
| `"Friendly"` | `"ALLOW ✅"` | Signal is safe — no action required |
| `"Unknown"` | `"MONITOR 👁️"` | Signal is unverified — flag for observation |
| `"Hostile"` | `"BLOCK 🚨"` | Signal is a threat — initiate countermeasures |

#### Example

```python
from backend import defense_action

action = defense_action("Hostile")
print(action)  # "BLOCK 🚨"

action = defense_action("Friendly")
print(action)  # "ALLOW ✅"
```

---

## End-to-End Usage

```python
from backend import classify_signal, defense_action

# Incoming signal parameters
freq     = 150_000_000   # 150 MHz
strength = 0.92
noise    = 0.05

# Step 1 — Classify
label, confidence = classify_signal(freq, strength, noise)

# Step 2 — Respond
action = defense_action(label)

print(f"Classification : {label}")
print(f"Confidence     : {confidence}%")
print(f"Defense Action : {action}")
```

**Output:**
```
Classification : Hostile
Confidence     : 96.5%
Defense Action : BLOCK 🚨
```

---

## Model

| Property | Value |
|----------|-------|
| File | `model.pkl` |
| Algorithm | Random Forest Classifier |
| Estimators | 200 trees |
| Features | `norm_freq`, `Signal Strength` |
| Classes | `Friendly`, `Unknown`, `Hostile` |
| Loader | `joblib.load("model.pkl")` |

The model is loaded once at module import time and reused for all subsequent inference calls.

---

## Gemini AI Integration

The dashboard (`app.py`) additionally calls the **Google Gemini API** directly to generate natural-language threat briefings. This is handled in `app.py` via the `call_gemini()` function and is not part of the `backend.py` module.

### Endpoint

```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent
```

### Trigger Conditions

- Manual scan with a Gemini API key configured in the sidebar
- After an Attack Simulation completes (if "Generate AI Threat Brief" is checked)

### Offline Mode

If no API key is provided, the dashboard operates in **Offline Mode** — all ML classification, defense actions, and visualizations remain fully functional. Only the AI threat brief is unavailable.

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| `freq` outside 70–160 MHz | `norm_freq` is clamped to `[0, 100]` — no exception raised |
| Invalid `label` passed to `defense_action()` | Returns `"BLOCK 🚨"` as a safe default (implicit else) |
| `model.pkl` not found | `joblib.load()` raises `FileNotFoundError` — retrain using `model.py` |
| Gemini API key invalid or missing | Dashboard falls back to Offline Mode silently |

---

## Retraining the Model

If you need to retrain on new data:

```bash
# 1. Add raw signal data to logged_data.csv
# 2. Normalize and label
python prepare_data.py

# 3. Retrain
python model.py

# 4. New model.pkl is generated — restart the app
streamlit run app.py
```

> ⚠️ Do not change `FREQ_MIN` / `FREQ_MAX` in `backend.py` without also updating `prepare_data.py` and retraining the model. Mismatched normalization will silently degrade classification accuracy.

---

<div align="center">
  <sub>RF SENTINEL SIGINT OPS v3.1 — Backend API Reference</sub>
</div>

