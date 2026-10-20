import { useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function ProfilePage({ user, setUser }) {
  const [form, setForm] = useState({
    name: user.name,
    city: user.city,
    state: user.state,
    profession: user.profession,
    language: user.language
  });
  const [message, setMessage] = useState("");

  async function submitProfile(event) {
    event.preventDefault();
    const { data } = await api.put(`/users/${user.id}`, form);
    setUser(data.user);
    localStorage.setItem("legalbuddy_user", JSON.stringify(data.user));
    setMessage("Profile updated.");
  }

  return (
    <div className="page split-grid">
      <div className="glass-card">
        <SectionHeader eyebrow="Settings" title="Profile" description="Manage personal details and preferences." />
        <form className="stack" onSubmit={submitProfile}>
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <div className="form-row">
            <input value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} />
            <input value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })} />
          </div>
          <div className="form-row">
            <select value={form.profession} onChange={(e) => setForm({ ...form, profession: e.target.value })}>
              <option>Student / Learner</option>
              <option>Need Legal Help</option>
              <option>Lawyer</option>
            </select>
            <select value={form.language} onChange={(e) => setForm({ ...form, language: e.target.value })}>
              <option>English</option>
              <option>Hindi</option>
            </select>
          </div>
          <button className="primary-button" type="submit">Save Changes</button>
          {message && <p className="success-text">{message}</p>}
        </form>
      </div>
      <div className="glass-card">
        <h3>Account Snapshot</h3>
        <p>Email: {user.email || "Not provided"}</p>
        <p>Phone: {user.phone || "Not provided"}</p>
        <p>Role: {user.role}</p>
      </div>
    </div>
  );
}
