import { useEffect, useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function LawyersPage() {
  const [lawyers, setLawyers] = useState([]);
  const [filters, setFilters] = useState({ case_type: "", location: "", budget: "" });

  async function loadLawyers(nextFilters = filters) {
    const params = new URLSearchParams();
    if (nextFilters.case_type) params.set("case_type", nextFilters.case_type);
    if (nextFilters.location) params.set("location", nextFilters.location);
    if (nextFilters.budget) params.set("budget", nextFilters.budget);
    const { data } = await api.get(`/public/lawyers?${params.toString()}`);
    setLawyers(data.items);
  }

  useEffect(() => {
    loadLawyers(filters);
  }, []);

  return (
    <div className="page stack">
      <SectionHeader eyebrow="Recommendations" title="Lawyer Recommendation" description="Static shortlist for now, ready to evolve into real verified listings." />
      <div className="toolbar">
        <input placeholder="Case type" value={filters.case_type} onChange={(e) => setFilters({ ...filters, case_type: e.target.value })} />
        <input placeholder="Location" value={filters.location} onChange={(e) => setFilters({ ...filters, location: e.target.value })} />
        <select value={filters.budget} onChange={(e) => setFilters({ ...filters, budget: e.target.value })}>
          <option value="">Any Budget</option>
          <option value="Moderate">Moderate</option>
          <option value="Premium">Premium</option>
        </select>
        <button className="primary-button" onClick={() => loadLawyers(filters)}>Filter</button>
      </div>
      <div className="content-grid">
        {lawyers.map((lawyer) => (
          <div key={lawyer.name} className="glass-card">
            <h3>{lawyer.name}</h3>
            <p>{lawyer.speciality}</p>
            <div className="meta-row">
              <span>{lawyer.location}</span>
              <span>{lawyer.budget}</span>
            </div>
            <p>{lawyer.bio}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
