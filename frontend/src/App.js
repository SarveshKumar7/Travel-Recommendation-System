import React, { useState } from "react";
import "./App.css";

function App() {
  const [inputs, setInputs] = useState({
    mood: "",
    climate: "",
    activity: "",
    budget: "",
  });
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setInputs({ ...inputs, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:5000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(inputs),
      });
      const data = await res.json();
      setRecommendations(data);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    } finally {
      setLoading(false);
    }
  };

  // Function to safely generate Unsplash image URL
  const getImageUrl = (city, country) => {
    const query = encodeURIComponent(`${city} ${country} travel`);
    return `https://source.unsplash.com/400x200/?${query}`;
  };

  return (
    <div className="App">
      <h1 className="title">🌍 Travel Recommender System</h1>

      <form onSubmit={handleSubmit} className="form-container">
        {["mood", "climate", "activity", "budget"].map((field) => (
          <select
            key={field}
            name={field}
            onChange={handleChange}
            required
            className="custom-select"
          >
            <option value="">
              {field.charAt(0).toUpperCase() + field.slice(1)}
            </option>
            {field === "mood" && (
              <>
                <option value="relaxing">Relaxing</option>
                <option value="adventure">Adventure</option>
                <option value="romantic">Romantic</option>
                <option value="cultural">Cultural</option>
                <option value="party">Party</option>
              </>
            )}
            {field === "climate" && (
              <>
                <option value="warm">Warm</option>
                <option value="cold">Cold</option>
                <option value="tropical">Tropical</option>
                <option value="moderate">Moderate</option>
              </>
            )}
            {field === "activity" && (
              <>
                <option value="beach">Beach</option>
                <option value="mountain">Mountain</option>
                <option value="urban">Urban</option>
                <option value="nature">Nature</option>
              </>
            )}
            {field === "budget" && (
              <>
                <option value="Budget">Budget</option>
                <option value="Mid-range">Mid-range</option>
                <option value="Luxury">Luxury</option>
              </>
            )}
          </select>
        ))}

        <button type="submit" className="btn-submit">Get Recommendations</button>
      </form>

      {loading && <div className="loader">Loading...</div>}

      <div className="results">
        {recommendations.map((rec, idx) => (
          <div key={idx} className="card">
            <img
              src={getImageUrl(rec.city, rec.country)}
              alt={rec.city}
              className="card-image"
              onError={(e) => {
                e.target.src =
                  "https://via.placeholder.com/400x200?text=No+Image"; // fallback image
              }}
            />
            <div className="card-content">
              <h2>{rec.city}, {rec.country}</h2>
              <p><b>About:</b> {rec.about}</p>
              <p><b>Budget:</b> {rec.budget} | {rec.estimated_cost}</p>
              <p><b>Rating:</b> {rec.rating} / 5</p>
              <p><b>Match Score:</b> {rec.score.toFixed(3)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;