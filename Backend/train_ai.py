import pandas as pd
import numpy as np
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, IsolationForest
import joblib

print("⏳ Loading Dataset...")
try:
    dataset = load_dataset("notesbymuneeb/ai-waf-dataset")
    df = pd.DataFrame(dataset['train'])
    print("✅ Dataset Loaded Successfully")
except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    exit()

# --- FIX 1: Force Labels to be Integers ---
print("⚙️  Processing Labels...")
# This converts "0" (text) to 0 (number) to fix the error
df['label'] = pd.to_numeric(df['label'], errors='coerce').fillna(0).astype(int)

# 1. Feature Extraction
print("⚙️  Extracting Features...")
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3), max_features=2000)
X = vectorizer.fit_transform(df['text'])
y = df['label']

# 2. Train Random Forest (Known Attacks)
print("🧠 Training Random Forest (Known Attacks)...")
rf_model = RandomForestClassifier(n_estimators=100, n_jobs=-1)
rf_model.fit(X, y)

# 3. Train Isolation Forest (Zero-Day)
print("🧠 Training Isolation Forest (Zero-Day Detection)...")

# --- FIX 2: The Safety Filter ---
# We filter for label 0 (Safe). 
# We use .values to make sure it matches the matrix format.
safe_traffic = X[(y == 0).values]

# SAFETY CHECK: If for some reason filter fails, use all data to prevent crash
if safe_traffic.shape[0] == 0:
    print("⚠️ Warning: No safe traffic found in filter. Using all data for Isolation Forest.")
    safe_traffic = X

iso_model = IsolationForest(contamination=0.05, random_state=42)
iso_model.fit(safe_traffic)

# 4. Save Models
print("💾 Saving Models...")
joblib.dump(rf_model, "rf_model.pkl")
joblib.dump(iso_model, "iso_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("✅ System Ready: Models Saved successfully.")