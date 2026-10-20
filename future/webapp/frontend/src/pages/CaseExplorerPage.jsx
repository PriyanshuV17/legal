import { useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function CaseExplorerPage({ user }) {
  const [query, setQuery] = useState("");
  const [year, setYear] = useState("");
  const [cases, setCases] = useState([]);

  async function searchCases(event) {
    event.preventDefault();
    const { data } = await api.get(`/public/cases?query=${encodeURIComponent(query)}&year=${encodeURIComponent(year)}`);
    setCases(data.items);
  }

  async function saveCase(item) {
    await api.post(`/users/${user.id}/saved-cases`, item);
  }

  return (
    <div className="page stack">
      <SectionHeader eyebrow="Research" title="Case Explorer" description="Search by keyword or year, then save relevant judgments." />
      <form className="toolbar" onSubmit={searchCases}>
        <input placeholder="Search cases" value={query} onChange={(e) => setQuery(e.target.value)} />
        <input placeholder="Year" value={year} onChange={(e) => setYear(e.target.value)} />
        <button className="primary-button" type="submit">Search</button>
      </form>
      <div className="content-grid">
        {cases.map((item) => (
          <div key={`${item.title}-${item.year}`} className="glass-card">
            <h3>{item.title}</h3>
            <p>{item.year}</p>
            <div className="button-row">
              <a className="secondary-button" href={`http://127.0.0.1:8001/api/files/judgment?file=${item.file}&year=${item.year}`} target="_blank" rel="noreferrer">Open PDF</a>
              <button className="ghost-button" onClick={() => saveCase(item)}>Save Case</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
