import { useEffect, useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

const initialForm = {
  name: "",
  email: "",
  phone: "",
  speciality: "",
  location: "",
  budget: "Moderate",
  verified: false,
  bio: ""
};

export default function AdminLawyersPage() {
  const [lawyers, setLawyers] = useState([]);
  const [form, setForm] = useState(initialForm);

  async function loadLawyers() {
    const { data } = await api.get("/admin/lawyers");
    setLawyers(data.items);
  }

  useEffect(() => {
    loadLawyers();
  }, []);

  async function createLawyer(event) {
    event.preventDefault();
    await api.post("/admin/lawyers", form);
    setForm(initialForm);
    loadLawyers();
  }

  async function toggleVerify(item) {
    await api.patch(`/admin/lawyers/${item.id}`, { verified: !item.verified });
    loadLawyers();
  }

  return (
    <div className="page split-grid">
      <div className="glass-card">
        <SectionHeader eyebrow="Admin" title="Lawyer Management" description="Add and verify lawyers for future booking flows." />
        <form className="stack" onSubmit={createLawyer}>
          <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <div className="form-row">
            <input placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <input placeholder="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </div>
          <div className="form-row">
            <input placeholder="Speciality" value={form.speciality} onChange={(e) => setForm({ ...form, speciality: e.target.value })} />
            <input placeholder="Location" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
          </div>
          <div className="form-row">
            <select value={form.budget} onChange={(e) => setForm({ ...form, budget: e.target.value })}>
              <option>Budget</option>
              <option>Moderate</option>
              <option>Premium</option>
            </select>
            <select value={String(form.verified)} onChange={(e) => setForm({ ...form, verified: e.target.value === "true" })}>
              <option value="false">Unverified</option>
              <option value="true">Verified</option>
            </select>
          </div>
          <textarea rows="4" placeholder="Bio" value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} />
          <button className="primary-button" type="submit">Add Lawyer</button>
        </form>
      </div>
      <div className="glass-card">
        <h3>Current Lawyers</h3>
        {lawyers.map((item) => (
          <div className="list-row" key={item.id}>
            <div>
              <span>{item.name}</span>
              <small>{item.speciality} | {item.location} | {item.budget}</small>
            </div>
            <button className="ghost-button" onClick={() => toggleVerify(item)}>
              {item.verified ? "Unverify" : "Verify"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
