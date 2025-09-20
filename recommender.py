import pandas as pd
import json
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

# ---- Load datasets ----
world_df = pd.read_csv("worldwide_cities.csv")
india_df = pd.read_csv("india_cities.csv")

# Merge both datasets
df = pd.concat([world_df, india_df], ignore_index=True)

# ---- Parse avg_temp_monthly into yearly average ----
def extract_avg_temp(val):
    try:
        data = json.loads(val.replace("'", '"'))  # convert string dict → json
        avgs = [month["avg"] for month in data.values()]
        return sum(avgs) / len(avgs)
    except:
        return None

df["avg_temp_yearly"] = df["avg_temp_monthly"].apply(extract_avg_temp)

# ---- Map budget levels to numbers ----
budget_map = {"Budget": 1, "Mid-range": 2, "Luxury": 3}
df["budget_level_num"] = df["budget_level"].map(budget_map)

# ---- Features for model ----
features = [
    "avg_temp_yearly", "budget_level_num",
    "culture", "adventure", "nature", "beaches",
    "nightlife", "cuisine", "wellness", "urban", "seclusion"
]

df = df.dropna(subset=features)

# ---- Normalize features ----
scaler = StandardScaler()
X = scaler.fit_transform(df[features])

# ---- Ask user for preferences ----
def get_preferences():
    print("🌍 Welcome to Travel Recommender!")
    
    mood = input("Choose your mood (relaxing / adventure / romantic / cultural / party): ").lower()
    climate = input("Preferred climate (warm / cold / tropical / moderate): ").lower()
    activity = input("Do you prefer beach, mountain, urban, or nature? ").lower()
    budget = input("Budget level (Budget / Mid-range / Luxury): ").title()
    
    mood_weights = {
        "relaxing": {"wellness": 1.5, "nature": 1.2},
        "adventure": {"adventure": 1.5, "nature": 1.3},
        "romantic": {"culture": 1.3, "nature": 1.2},
        "cultural": {"culture": 1.5, "urban": 1.2},
        "party": {"nightlife": 1.6, "urban": 1.2}
    }
    
    prefs = {col: 0 for col in features}
    
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
    
    return prefs

# ---- Recommend destinations ----
def recommend_from_prefs(prefs, top_n=5):
    user_vector = [prefs.get(col, 0) for col in features]
    user_vector = scaler.transform([user_vector])
    
    similarity_scores = cosine_similarity(user_vector, X)[0]
    
    budget_value = prefs.get("budget_level_num", 2)
    filtered_df = df[df["budget_level_num"] == budget_value].copy()
    
    if filtered_df.empty:
        print("⚠️ No cities found with the chosen budget level. Showing top recommendations anyway.")
        top_indices = similarity_scores.argsort()[::-1][:top_n]
        recommendations = df.iloc[top_indices]
        recommendations["score"] = similarity_scores[top_indices]
    else:
        filtered_indices = filtered_df.index
        filtered_scores = similarity_scores[filtered_indices]
        top_filtered_indices = filtered_scores.argsort()[::-1][:top_n]
        recommendations = filtered_df.iloc[top_filtered_indices].copy()
        recommendations["score"] = filtered_scores[top_filtered_indices]
    
    cost_map = {
        "Budget": "$500 - $1000",
        "Mid-range": "$1000 - $2500",
        "Luxury": "$2500 - $5000+"
    }
    recommendations["Estimated Cost"] = recommendations["budget_level"].map(cost_map)
    
    recommendations["Rating (/5)"] = recommendations[
        ["culture", "adventure", "nightlife", "nature"]
    ].mean(axis=1).round(1)
    
    return recommendations

# ---- Display results in Travel Card style ----
def display_recommendations(recommendations):
    print("\n🌍 Top Travel Recommendations for You\n")
    
    for idx, row in recommendations.iterrows():
        print(f"✨ Recommendation #{idx+1}")
        print(f"🏙 City: {row['city']}")
        print(f"🌍 Country: {row['country']} ({row['region']})")
        print(f"📖 About: {row['short_description']}")
        print(f"💰 Budget: {row['budget_level']} | Estimated Cost: {row['Estimated Cost']}")
        print(f"⭐ Rating: {row['Rating (/5)']} / 5")
        print(f"📊 Match Score: {round(row['score'], 3)}")
        print("-" * 50)

# ---- Run system ----
if __name__ == "__main__":
    prefs = get_preferences()
    recs = recommend_from_prefs(prefs, top_n=5)
    display_recommendations(recs)
