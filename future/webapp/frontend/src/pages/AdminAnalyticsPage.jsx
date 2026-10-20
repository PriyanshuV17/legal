import { useEffect, useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function AdminAnalyticsPage() {
  const [analytics, setAnalytics] = useState({ top_queries: [], case_types: [] });

  useEffect(() => {
    api.get("/admin/analytics").then(({ data }) => setAnalytics(data));
  }, []);

  return (
    <div className="page split-grid">
      <div className="glass-card">
        <SectionHeader eyebrow="Admin" title="Top Queries" />
        {analytics.top_queries.map((item) => (
          <div className="list-row" key={item.query}>
            <span>{item.query}</span>
            <small>{item.count}</small>
          </div>
        ))}
      </div>
      <div className="glass-card">
        <SectionHeader eyebrow="Admin" title="Case Trends" />
        {analytics.case_types.map((item) => (
          <div className="list-row" key={item.name}>
            <span>{item.name}</span>
            <small>{item.count}</small>
          </div>
        ))}
      </div>
    </div>
  );
}
