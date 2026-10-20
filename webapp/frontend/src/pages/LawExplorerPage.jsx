import { useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function LawExplorerPage({ user }) {
  const [query, setQuery] = useState("");
  const [laws, setLaws] = useState([]);

  async function searchLaws(event) {
    event.preventDefault();
    const { data } = await api.get(`/public/laws?query=${encodeURIComponent(query)}`);
    setLaws(data.items);
  }

  async function saveLaw(item) {
    await api.post(`/users/${user.id}/saved-laws`, item);
  }

  return (
    <div className="page stack">
      <SectionHeader eyebrow="Knowledge Base" title="Law Explorer" description="Search statutory sections and bookmark the ones you revisit often." />
      <form className="toolbar" onSubmit={searchLaws}>
        <input placeholder="Search IPC, BNS, Article..." value={query} onChange={(e) => setQuery(e.target.value)} />
        <button className="primary-button" type="submit">Search</button>
      </form>
      <div className="content-grid">
        {laws.map((item) => (
          <div key={item.section_code} className="glass-card">
            <h3>{item.title}</h3>
            <p>{item.description}</p>
            <div className="button-row">
              <span className="tag">{item.section_code}</span>
              <button className="ghost-button" onClick={() => saveLaw(item)}>Bookmark</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
