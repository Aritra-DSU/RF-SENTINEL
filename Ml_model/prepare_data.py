import pandas as pd

df = pd.read_csv("logged_data.csv")

# 🔥 Normalize Frequency (VERY IMPORTANT)
f_min = df["Frequency"].min()
f_max = df["Frequency"].max()

df["norm_freq"] = (df["Frequency"] - f_min) / (f_max - f_min) * 100

# ✅ Create labels based on normalized freq
def create_label(row):
    f = row["norm_freq"]

    if f < 33:
        return "Friendly"
    elif f < 66:
        return "Unknown"
    else:
        return "Hostile"

df["label"] = df.apply(create_label, axis=1)

# ✅ DEBUG (IMPORTANT)
print("\nLabel Distribution:")
print(df["label"].value_counts())

# SAVE
df.to_csv("labeled_data.csv", index=False)

print("\n✅ labeled_data.csv created")