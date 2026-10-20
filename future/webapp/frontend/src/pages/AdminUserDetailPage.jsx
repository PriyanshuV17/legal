import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function AdminUserDetailPage() {
  const { userId } = useParams();
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get(`/admin/users/${userId}`).then(({ data }) => setData(data));
  }, [userId]);

  if (!data) return <div className="page">Loading user detail...</div>;

  return (
    <div className="page stack">
      <SectionHeader
        eyebrow="Admin User Detail"
        title={data.user.name}
        description="Profile, sessions, and recent query history for this account."
        action={<Link className="secondary-button" to="/admin">Back to Admin</Link>}
      />
      <div className="split-grid">
        <div className="glass-card">
          <h3>Profile</h3>
          <p>Email: {data.user.email || "Not provided"}</p>
          <p>Phone: {data.user.phone || "Not provided"}</p>
          <p>Location: {data.user.city}, {data.user.state}</p>
          <p>Profession: {data.user.profession}</p>
          <p>Role: {data.user.role}</p>
          <p>Status: {data.user.is_active ? "Active" : "Inactive"}</p>
        </div>
        <div className="glass-card">
          <h3>Chat Sessions</h3>
          {data.sessions.map((session) => (
            <div className="list-row" key={session.id}>
              <span>{session.title}</span>
              <small>{new Date(session.updated_at).toLocaleString()}</small>
            </div>
          ))}
        </div>
      </div>
      <div className="glass-card">
        <h3>Recent Messages</h3>
        {data.messages.map((message) => (
          <div key={message.id} className="list-row">
            <span>{message.role}: {message.content.slice(0, 90)}</span>
            <small>{new Date(message.created_at).toLocaleString()}</small>
          </div>
        ))}
      </div>
    </div>
  );
}
