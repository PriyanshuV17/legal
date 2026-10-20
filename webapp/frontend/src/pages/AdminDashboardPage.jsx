import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";
import StatCard from "../components/StatCard";

export default function AdminDashboardPage() {
  const [overview, setOverview] = useState(null);
  const [users, setUsers] = useState([]);
  const [analytics, setAnalytics] = useState({ top_queries: [], case_types: [] });

  useEffect(() => {
    api.get("/admin/overview").then(({ data }) => setOverview(data));
    api.get("/admin/users").then(({ data }) => setUsers(data.items));
    api.get("/admin/analytics").then(({ data }) => setAnalytics(data));
  }, []);

  if (!overview) return <div className="page">Loading admin dashboard...</div>;

  return (
    <div className="page stack">
      <SectionHeader eyebrow="Admin" title="Platform Control Center" description="Monitor users, system usage, bookings, and query trends." />
      <div className="stats-grid">
        <StatCard label="Users" value={overview.totals.users} helper="Registered accounts" />
        <StatCard label="Queries" value={overview.totals.queries} helper="Tracked in chat logs" />
        <StatCard label="Bookings" value={overview.totals.bookings} helper="Consultation requests" />
        <StatCard label="Contacts" value={overview.totals.contacts} helper="Inbound support" />
      </div>
      <div className="split-grid">
        <div className="glass-card">
          <h3>Users</h3>
          {users.slice(0, 8).map((user) => (
            <div className="list-row" key={user.id}>
              <Link to={`/admin/users/${user.id}`}>{user.name}</Link>
              <small>{user.query_count} queries</small>
            </div>
          ))}
        </div>
        <div className="glass-card">
          <h3>Recent Activity</h3>
          {overview.recent_logs.map((log) => (
            <div className="list-row" key={log.id}>
              <span>{log.event_type}</span>
              <small>{log.detail}</small>
            </div>
          ))}
        </div>
      </div>
      <div className="split-grid">
        <div className="glass-card">
          <h3>Top Queries</h3>
          {analytics.top_queries.map((item) => (
            <div key={item.query} className="list-row">
              <span>{item.query}</span>
              <small>{item.count}</small>
            </div>
          ))}
        </div>
        <div className="glass-card">
          <h3>Case Trends</h3>
          {analytics.case_types.map((item) => (
            <div key={item.name} className="list-row">
              <span>{item.name}</span>
              <small>{item.count}</small>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
