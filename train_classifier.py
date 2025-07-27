import pandas as pd
import pickle
from pathlib import Path
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.utils import resample

csv_path = Path("training_data.csv")

if not csv_path.exists():
    raise FileNotFoundError("❌ training_data.csv not found! Run data collection first.")

data = pd.read_csv(csv_path)
data = data.drop_duplicates()

valid_labels = {"BODY", "TITLE", "H1", "H2", "H3"}
data = data[data["label"].isin(valid_labels)]

if data.empty:
    raise ValueError("❌ No valid labeled rows found in training_data.csv")

# ---------- BALANCE THE DATASET ----------
body = data[data["label"] == "BODY"]
non_body = data[data["label"] != "BODY"]

body_downsampled = resample(
    body,
    replace=False,
    n_samples=min(len(non_body) * 2, len(body)),
    random_state=42
)

data_balanced = pd.concat([body_downsampled, non_body])
data_balanced = data_balanced.sample(frac=1, random_state=42)

print(f"✅ Original rows: {len(data)}, Balanced rows: {len(data_balanced)}")

# ---------- TRAINING ----------
features = [
    "font_size", "bold", "indent", "length", "numbered",
    "is_all_caps", "upper_ratio", "ends_with_colon",
    "word_count", "is_page1"
]
X = data_balanced[features].values

label_map = {"BODY": 0, "TITLE": 1, "H1": 2, "H2": 3, "H3": 4}
y = data_balanced["label"].map(label_map).values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

clf = XGBClassifier(
    n_estimators=250,
    learning_rate=0.05,
    max_depth=7,
    random_state=42,
    use_label_encoder=False,
    eval_metric="mlogloss"
)

print("⏳ Training enhanced XGBoost model...")
clf.fit(X_train, y_train)

model_dir = Path("models")
model_dir.mkdir(exist_ok=True)
model_path = model_dir / "heading_classifier.pkl"

with open(model_path, "wb") as f:
    pickle.dump(clf, f)

print(f"✅ Enhanced XGBoost classifier trained and saved to {model_path}")
