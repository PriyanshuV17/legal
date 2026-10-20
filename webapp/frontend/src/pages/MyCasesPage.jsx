import { useEffect, useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function MyCasesPage({ user }) {
  const [saved, setSaved] = useState({ cases: [], laws: [] });

  useEffect(() => {
    api.get(`/users/${user.id}/saved`).then(({ data }) => setSaved(data));
  }, [user]);

  return (
    <div className="page split-grid">
      <div className="glass-card">
        <SectionHeader eyebrow="Workspace" title="Saved Cases" />
        {saved.cases.map((item) => (
          <div key={item.id} className="list-row">
            <span>{item.title}</span>
            <small>{item.year}</small>
          </div>
        ))}
      </div>
      <div className="glass-card">
        <SectionHeader eyebrow="Workspace" title="Saved Laws" />
        {saved.laws.map((item) => (
          <div key={item.id} className="list-row">
            <span>{item.title}</span>
            <small>{item.section_code}</small>
          </div>
        ))}
      </div>
    </div>
  );
}
