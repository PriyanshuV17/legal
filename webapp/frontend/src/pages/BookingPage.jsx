import { useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function BookingPage({ user }) {
  const [form, setForm] = useState({
    lawyer_name: "Aarav Mehta",
    case_type: "Criminal",
    mode: "Online",
    date: "",
    time_slot: "",
    notes: ""
  });
  const [message, setMessage] = useState("");

  async function submitBooking(event) {
    event.preventDefault();
    await api.post("/bookings", { user_id: user.id, ...form });
    setMessage("Consultation request saved.");
  }

  return (
    <div className="page split-grid">
      <div className="glass-card">
        <SectionHeader eyebrow="Future Ready" title="Book a Lawyer" description="The UI is live now. Workflow and payments can be layered in next." />
        <form className="stack" onSubmit={submitBooking}>
          <input value={form.lawyer_name} onChange={(e) => setForm({ ...form, lawyer_name: e.target.value })} placeholder="Lawyer name" />
          <div className="form-row">
            <select value={form.case_type} onChange={(e) => setForm({ ...form, case_type: e.target.value })}>
              <option>Criminal</option>
              <option>Family</option>
              <option>Civil</option>
              <option>Corporate</option>
            </select>
            <select value={form.mode} onChange={(e) => setForm({ ...form, mode: e.target.value })}>
              <option>Online</option>
              <option>Offline</option>
            </select>
          </div>
          <div className="form-row">
            <input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
            <input type="time" value={form.time_slot} onChange={(e) => setForm({ ...form, time_slot: e.target.value })} />
          </div>
          <textarea rows="4" placeholder="Notes for the lawyer" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          <button className="primary-button" type="submit">Book Consultation</button>
          {message && <p className="success-text">{message}</p>}
        </form>
      </div>
      <div className="glass-card">
        <h3>What gets stored</h3>
        <ul className="clean-list">
          <li>User id and lawyer selection</li>
          <li>Date, time, mode, and notes</li>
          <li>Status for admin review</li>
          <li>Audit event for operational tracking</li>
        </ul>
      </div>
    </div>
  );
}
