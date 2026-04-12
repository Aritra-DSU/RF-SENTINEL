RF SENTINEL — SIGINT OPS

> **AI-powered Radio Frequency threat detection and defense system for real-time signal intelligence.**

RF Sentinel is a military-grade SIGINT (Signals Intelligence) operations dashboard that uses a trained Machine Learning model to classify RF signals as **Friendly**, **Unknown**, or **Hostile** — and triggers automated defense actions in real time. Built with Streamlit, scikit-learn, and the Gemini AI API.

---

 🖥️ Demo

> ## 🖥️ Demo

Run locally with:

```bash
streamlit run app.py
```

Then open your browser at **http://localhost:8501/**

---

 🚀 Features

- Real-Time Signal Classification — Classifies RF signals (70–160 MHz) as Friendly, Unknown, or Hostile using a trained Random Forest model
- Automated Defense Actions — Instantly responds with `ALLOW ✅`, `MONITOR 👁️`, or `BLOCK 🚨` based on classification
- AI Threat Analysis — Integrates with Google Gemini API to generate natural-language tactical threat briefings
- Live Monitoring Model — Continuously scans and classifies signals in real time
- Attack Scenario Simulator — Simulates 5 real-world attack types (Coordinated Jamming, Frequency Hopping, IFF Spoofing, etc.) at configurable intensity levels
- Radar & Waterfall Display — Visual radar with animated blip tracking and spectrum waterfall visualization
- Threat Timeline — Live-updating graph of threat levels over session history
- Geo Signal Mapping — Plots detected signals on a geographic map
- Event Log with Export — Full filterable event log exportable as CSV or JSON
- Red Alert Overlay — Full-screen red alert with audio alarm when threat level exceeds 75%
- Band Reference Panel — Sidebar reference for VHF-LOW, FM-BAND, VHF-HIGH, and MILITARY frequency bands

---

 🏗️ Project Structure

```
rf-sentinel/
│
├── app.py              # Main Streamlit UI — all tabs, visualizations, live monitoring
├── backend.py          # ML inference engine — signal classification & defense logic
├── model.py            # Model training script — Random Forest classifier
├── model.pkl           # Pre-trained serialized model (joblib)
├── prepare_data.py     # Data preprocessing — normalization & labeling
├── check_data.py       # Dataset inspection utility
├── logged_data.csv     # Raw RF signal logs (input to prepare_data.py)
└── labeled_data.csv    # Processed & labeled dataset (output of prepare_data.py)
```

---

⚙️ How It Works

 1. Data Pipeline

Raw RF signal data (`logged_data.csv`) is processed by `prepare_data.py`:

- Frequency normalization — Raw frequency (Hz) is scaled to a 0–100 range based on the observed min/max (70 MHz – 160 MHz)
- Label generation — Signals are labeled based on normalized frequency:
  - `norm_freq < 33` → Friendly
  - `33 ≤ norm_freq < 66` → Unknown
  - `norm_freq ≥ 66` → Hostile

 2. Model Training (`model.py`)

- Algorithm: Random Forest Classifier (`n_estimators=200`)
- Features: `norm_freq` (normalized frequency) + `Signal Strength`
- Target: `label` (Friendly / Unknown / Hostile)
- Split: 80/20 train-test split
- Output: Serialized to `model.pkl` via joblib

 3. Inference (`backend.py`)

At runtime, incoming signals are:
1. Normalized using the same fixed min/max constants (`FREQ_MIN=70 MHz`, `FREQ_MAX=160 MHz`)
2. Fed into the loaded model for classification
3. Confidence score extracted from `predict_proba()`
4. Defense action determined from the classification label

### 4. Dashboard (`app.py`)

Seven operational tabs:

| Tab | Description |
|-----|-------------|
|  OPS CENTER | Main scan panel — manual signal scan with live result display |
|  RADAR | Animated radar with signal blip tracking |
|  LIVE MONITOR | Continuous auto-scanning mode |
|  WATERFALL | Spectrum waterfall visualization |
|  TIMELINE | Threat level history graph |
|  ATTACK SIM | Simulate real-world attack scenarios with AI brief |
|  EVENT LOG | Full filterable event log with CSV/JSON export |

---

 📡 Frequency Band Reference

| Band | Range | Usage |
|------|-------|-------|
| VHF-LOW | 70–88 MHz | Comms / Recon |
| FM-BAND | 88–108 MHz | Civil / Spoof |
| VHF-HIGH | 108–137 MHz | Aviation / Nav |
| MILITARY | 137–160 MHz | Tactical / SAT |

---

🛠️ Installation & Setup

 Prerequisites

- Python 3.8+
- pip

 1. Clone the Repository

```bash
git clone https://github.com/Samriddha02/RF_Sentinel.git
cd RF_Sentinel
```

 2. Install Dependencies

```bash
pip install streamlit scikit-learn joblib pandas requests
```

 3. Prepare Data & Train Model (Optional — `model.pkl` is pre-trained)

```bash
# Step 1: Inspect your raw data
python check_data.py

# Step 2: Normalize and label the data
python prepare_data.py

# Step 3: Train the model
python model.py
```

 4. Run the App

```bash
streamlit run app.py
```

 5. (Optional) Enable AI Threat Briefs

Enter your **Google Gemini API key** in the sidebar when the app is running. Without a key, the app runs in **Offline Mode** — all ML classification and defense features remain fully functional.

---

🧠 ML Model Details

| Parameter | Value |
|-----------|-------|
| Algorithm | Random Forest Classifier |
| Estimators | 200 trees |
| Features | `norm_freq`, `Signal Strength` |
| Classes | Friendly, Unknown, Hostile |
| Normalization | Min-Max (70 MHz – 160 MHz → 0–100) |
| Serialization | joblib (`model.pkl`) |

---

## 📂 Dataset

The raw RF signal log used to train this model is available here:

👉 **[Download logged_data.csv](https://drive.google.com/drive/folders/19De4JpluyRz1xtVQkkbjRdk0iIAG9wje?usp=drive_linkhttps://drive.google.com/drive/folders/19De4JpluyRz1xtVQkkbjRdk0iIAG9wje?usp=sharing)**

> Import this file into the project root before running `prepare_data.py`.

---

🔴 Alert System

- Threat Level < 50% — Normal operations
- Threat Level 50–74% — Elevated monitoring
- Threat Level ≥ 75% — RED ALERT — Full-screen overlay + audio alarm + scrolling ticker

---

🎮 Attack Scenarios (Simulator)

| Scenario | Frequency Range |
|----------|----------------|
| Coordinated Jamming | 137–160 MHz |
| Frequency Hopping Burst | 70–160 MHz (full sweep) |
| Low & Slow Infiltration | 70–108 MHz |
| Broadband Flood | 70–160 MHz |
| IFF Spoofing Probe | 108–137 MHz |

Each scenario supports intensity levels: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` — and optionally generates an AI tactical brief post-simulation.

---

📦 Dependencies

| Library | Purpose |
|---------|---------|
| `streamlit` | Web dashboard UI |
| `scikit-learn` | Random Forest ML model |
| `joblib` | Model serialization |
| `pandas` | Data processing |
| `requests` | Gemini API integration |

---

🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---


📁 Documentation

- 📊 Architecture: docs/architecture.png  
- 📡 API Docs: docs/api_docs.md  
