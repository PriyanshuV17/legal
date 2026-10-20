import { useEffect, useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function LawyersPage({ user }) {
  const [lawyers, setLawyers] = useState([]);
  const [filters, setFilters] = useState({ 
    state: user?.state || "",
    city: user?.city || "",
    language: user?.language || "English",
    specialization: ""
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function loadRecommendations(nextFilters = filters) {
    setLoading(true);
    setMessage("");
    try {
      const params = new URLSearchParams();
      if (nextFilters.state) params.set("state", nextFilters.state);
      if (nextFilters.city) params.set("city", nextFilters.city);
      if (nextFilters.language) params.set("language", nextFilters.language);
      if (nextFilters.specialization) params.set("specialization", nextFilters.specialization);
      if (user?.id) params.set("user_id", user.id);
      
      const { data } = await api.get(`/lawyers/recommend?${params.toString()}`);
      setLawyers(data.recommendations || []);
      if (data.count === 0) {
        setMessage("No lawyers found matching your criteria. Try adjusting filters.");
      }
    } catch (error) {
      setMessage("Error loading lawyer recommendations. Please try again.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  async function searchLawyers(nextFilters = filters) {
    if (!nextFilters.specialization?.trim()) {
      setMessage("Please enter a search query");
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const params = new URLSearchParams();
      params.set("query", nextFilters.specialization);
      if (nextFilters.state) params.set("state", nextFilters.state);
      if (nextFilters.city) params.set("city", nextFilters.city);
      if (nextFilters.language) params.set("language", nextFilters.language);
      if (user?.id) params.set("user_id", user.id);
      
      const { data } = await api.get(`/lawyers/search?${params.toString()}`);
      setLawyers(data.results || []);
      if (data.count === 0) {
        setMessage("No lawyers found matching your search. Try different keywords.");
      }
    } catch (error) {
      setMessage("Error searching lawyers. Please try again.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRecommendations(filters);
  }, [user?.id]);

  return (
    <div className="page stack">
      <SectionHeader 
        eyebrow="ML-Powered" 
        title="Lawyer Recommendations" 
        description="Find the best lawyers ranked by experience, rating, and your location." 
      />
      
      <div className="toolbar">
        <input 
          placeholder="State" 
          value={filters.state} 
          onChange={(e) => setFilters({ ...filters, state: e.target.value })} 
        />
        <input 
          placeholder="City" 
          value={filters.city} 
          onChange={(e) => setFilters({ ...filters, city: e.target.value })} 
        />
        <select 
          value={filters.language} 
          onChange={(e) => setFilters({ ...filters, language: e.target.value })}
        >
          <option value="English">English</option>
          <option value="Hindi">Hindi</option>
          <option value="Tamil">Tamil</option>
          <option value="Telugu">Telugu</option>
        </select>
        <input 
          placeholder="Search by specialization or name" 
          value={filters.specialization} 
          onChange={(e) => setFilters({ ...filters, specialization: e.target.value })} 
          onKeyDown={(e) => e.key === "Enter" && searchLawyers(filters)}
        />
        <button 
          className="primary-button" 
          onClick={() => loadRecommendations(filters)}
          disabled={loading}
        >
          {loading ? "Loading..." : "Filter"}
        </button>
        <button 
          className="secondary-button" 
          onClick={() => searchLawyers(filters)}
          disabled={loading}
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>

      {message && <p className={message.includes("Error") ? "error-text" : "info-text"}>{message}</p>}

      {lawyers.length === 0 && !loading && (
        <p className="info-text">No lawyers available. Try adjusting your search criteria.</p>
      )}

      <div className="content-grid">
        {lawyers.map((lawyer, idx) => (
          <div key={`${lawyer.name}-${idx}`} className="glass-card">
            <h3>{lawyer.name}</h3>
            <p className="speciality">{lawyer.type_of_lawyer || lawyer.specialization || "General Practice"}</p>
            <div className="meta-row">
              <span>{lawyer.state || lawyer.location}</span>
              <span>{lawyer.city}</span>
            </div>
            {lawyer.language && <div className="meta-row"><span>Language: {lawyer.language}</span></div>}
            {lawyer.experience_years && <div><strong>Experience:</strong> {lawyer.experience_years} years</div>}
            {lawyer.win_rate && <div><strong>Win Rate:</strong> {(lawyer.win_rate * 100).toFixed(1)}%</div>}
            {lawyer.fee_avg && <div><strong>Avg Fee:</strong> ₹{lawyer.fee_avg}</div>}
            <div className="button-group">
              <button className="primary-button" onClick={() => window.location.href = `/booking?lawyer=${lawyer.name}`}>
                Book Now
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
