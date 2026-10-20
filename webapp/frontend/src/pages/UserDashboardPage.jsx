import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";
import StatCard from "../components/StatCard";

export default function UserDashboardPage({ user }) {
  const [history, setHistory] = useState([]);
  const [saved, setSaved] = useState({ cases: [], laws: [] });

  useEffect(() => {
    if (!user) return;
    api.get(`/users/${user.id}/history`).then(({ data }) => setHistory(data.sessions));
    api.get(`/users/${user.id}/saved`).then(({ data }) => setSaved(data));
  }, [user]);

  return (
    <div className="page stack">
      <SectionHeader
        eyebrow="User Dashboard"
        title={`Welcome back, ${user?.name}`}
        description="Pick up where you left off, revisit your saved materials, or start a new legal conversation."
        action={<Link to="/chat" className="primary-button">Start Chat</Link>}
      />
      <div className="stats-grid">
        <StatCard label="Recent Chats" value={history.length} helper="Tracked in SQL" />
        <StatCard label="Saved Cases" value={saved.cases.length} helper="Your case workspace" />
        <StatCard label="Saved Laws" value={saved.laws.length} helper="Bookmarked sections" />
      </div>
      <div className="content-grid">
        <div className="glass-card">
          <h3>Quick Actions</h3>
          <div className="button-stack">
            <Link className="secondary-button" to="/cases">Explore Cases</Link>
            <Link className="secondary-button" to="/laws">Explore Laws</Link>
            <Link className="secondary-button" to="/booking">Book Consultation</Link>
          </div>
        </div>
        <div className="glass-card">
          <h3>Recent Chats</h3>
          {history.slice(0, 5).map((item) => (
            <div key={item.id} className="list-row">
              <span>{item.title}</span>
              <small>{new Date(item.updated_at).toLocaleString()}</small>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
