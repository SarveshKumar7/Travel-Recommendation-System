import pandas as pd
import json
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, mean_squared_error, accuracy_score
from flask import Flask, request, jsonify
from flask_cors import CORS

# ======================================================
# 1️⃣ LOAD AND MERGE DATASETS
# ======================================================
world_df = pd.read_csv("worldwide_cities.csv")
india_df = pd.read_csv("india_cities.csv")
df = pd.concat([world_df, india_df], ignore_index=True)

# ======================================================
# 2️⃣ TEMPERATURE PARSING
# ======================================================
def extract_avg_temp(val):
    try:
        data = json.loads(val.replace("'", '"'))
        avgs = [month["avg"] for month in data.values()]
        return sum(avgs) / len(avgs)
    except:
        return None

df["avg_temp_yearly"] = df["avg_temp_monthly"].apply(extract_avg_temp)

# ======================================================
# 3️⃣ ENCODING BUDGET LEVEL
# ======================================================
budget_map = {"Budget": 1, "Mid-range": 2, "Luxury": 3}
df["budget_level_num"] = df["budget_level"].map(budget_map)

# ======================================================
# 4️⃣ FEATURES AND NORMALIZATION
# ======================================================
features = [
    "avg_temp_yearly", "budget_level_num",
    "culture", "adventure", "nature", "beaches",
    "nightlife", "cuisine", "wellness", "urban", "seclusion"
]

df = df.dropna(subset=features)
scaler = StandardScaler()
X = scaler.fit_transform(df[features])
y = df["budget_level_num"].values

# ======================================================
# 5️⃣ MANUAL KNN IMPLEMENTATION
# ======================================================
def cosine_similarity_manual(a, b):
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot / (norm_a * norm_b + 1e-10)

def knn_recommend_manual(user_vector, X, df, k=5, budget_value=2):
    similarities = np.array([cosine_similarity_manual(user_vector, x) for x in X])
    df["similarity"] = similarities

    filtered_df = df[df["budget_level_num"] == budget_value]
    if filtered_df.empty:
        top_indices = similarities.argsort()[::-1][:k]
        recs = df.iloc[top_indices]
    else:
        recs = filtered_df.sort_values(by="similarity", ascending=False).head(k)
    return recs

# ---- OLD (library-based KNN) ----
# from sklearn.neighbors import NearestNeighbors
# knn_model = NearestNeighbors(n_neighbors=5, metric='cosine')
# knn_model.fit(X)

# ======================================================
# 6️⃣ MANUAL LOGISTIC REGRESSION IMPLEMENTATION
# ======================================================
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def manual_logistic_regression(X, y, lr=0.01, epochs=500):
    X = np.hstack([np.ones((X.shape[0], 1)), X])  # add bias term
    weights = np.zeros(X.shape[1])

    for epoch in range(epochs):
        z = np.dot(X, weights)
        predictions = sigmoid(z)
        gradient = np.dot(X.T, (predictions - y)) / y.size
        weights -= lr * gradient

    return weights

def predict_manual(X, weights):
    X = np.hstack([np.ones((X.shape[0], 1)), X])
    probs = sigmoid(np.dot(X, weights))
    preds = np.round(probs)
    return preds

# ---- OLD (library-based Logistic Regression) ----
# from sklearn.linear_model import LogisticRegression
# log_reg = LogisticRegression(max_iter=500)
# log_reg.fit(X_train_scaled, y_train)

# ======================================================
# 7️⃣ TRAIN MANUAL LOGISTIC REGRESSION
# ======================================================
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

weights = manual_logistic_regression(X_train, y_train, lr=0.05, epochs=1000)
y_pred = predict_manual(X_test, weights)

# Round predictions within valid range [1, 3]
y_pred = np.clip(y_pred, 1, 3)

# ======================================================
# 8️⃣ MODEL EVALUATION METRICS
# ======================================================
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
mse = mean_squared_error(y_test, y_pred)

print("\n✅ Training/Testing Results (Manual Logistic Regression)")
print(f"Accuracy : {acc*100:.2f}%")
print(f"Precision: {prec*100:.2f}%")
print(f"Recall   : {rec*100:.2f}%")
print(f"F1 Score : {f1*100:.2f}%")
print(f"MSE      : {mse:.4f}")

# ======================================================
# 9️⃣ FLASK RECOMMENDER API
# ======================================================
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

@app.route("/recommend", methods=["POST"])
def recommend_api():
    data = request.json
    prefs = {col: 0 for col in features}

    mood = data.get("mood", "").lower()
    climate = data.get("climate", "").lower()
    activity = data.get("activity", "").lower()
    budget = data.get("budget", "Mid-range").title()

    mood_weights = {
        "relaxing": {"wellness": 1.5, "nature": 1.2},
        "adventure": {"adventure": 1.5, "nature": 1.3},
        "romantic": {"culture": 1.3, "nature": 1.2},
        "cultural": {"culture": 1.5, "urban": 1.2},
        "party": {"nightlife": 1.6, "urban": 1.2}
    }

    if mood in mood_weights:
        for k, v in mood_weights[mood].items():
            prefs[k] = v

    if climate == "warm":
        prefs["avg_temp_yearly"] = 25
    elif climate == "cold":
        prefs["avg_temp_yearly"] = 5
    elif climate == "tropical":
        prefs["avg_temp_yearly"] = 28
    else:
        prefs["avg_temp_yearly"] = 15

    if activity == "beach":
        prefs["beaches"] = 1.5
    elif activity == "mountain":
        prefs["nature"] = 1.5
    elif activity == "urban":
        prefs["urban"] = 1.5
    elif activity == "nature":
        prefs["nature"] = 1.5

    prefs["budget_level_num"] = budget_map.get(budget, 2)

    user_vector = np.array([prefs.get(col, 0) for col in features])
    user_vector = scaler.transform([user_vector])[0]

    recs = knn_recommend_manual(user_vector, X, df, k=5, budget_value=prefs["budget_level_num"])

    cost_map = {"Budget": "$500 - $1000", "Mid-range": "$1000 - $2500", "Luxury": "$2500 - $5000+"}
    recs["Estimated Cost"] = recs["budget_level"].map(cost_map)
    recs["Rating (/5)"] = recs[["culture", "adventure", "nightlife", "nature"]].mean(axis=1).round(1)

    results = []
    for _, row in recs.iterrows():
        results.append({
            "city": row["city"],
            "country": row["country"],
            "region": row["region"],
            "about": row["short_description"],
            "budget": row["budget_level"],
            "estimated_cost": row["Estimated Cost"],
            "rating": float(row["Rating (/5)"]),
            "score": round(float(row["similarity"]), 3)
        })
    return jsonify(results)

# ======================================================
# 🔟 MAIN ENTRY POINT
# ======================================================
if __name__ == "__main__":
    app.run(debug=True, port=5000)
