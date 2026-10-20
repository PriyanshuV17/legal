import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function AdminUsersPage() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    api.get("/admin/users").then(({ data }) => setUsers(data.items));
  }, []);

  async function toggleUser(user) {
    const { data } = await api.patch(`/admin/users/${user.id}/status`, { is_active: !user.is_active });
    setUsers((prev) => prev.map((item) => (item.id === user.id ? { ...item, ...data.user } : item)));
  }

  return (
    <div className="page stack">
      <SectionHeader eyebrow="Admin" title="User Management" description="View users, usage, and activate or block accounts." />
      <div className="glass-card">
        {users.map((user) => (
          <div className="list-row" key={user.id}>
            <div>
              <Link to={`/admin/users/${user.id}`}>{user.name}</Link>
              <small>{user.email || user.phone || "No contact"} | {user.query_count} queries</small>
            </div>
            <button className="ghost-button" onClick={() => toggleUser(user)}>
              {user.is_active ? "Block" : "Activate"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
