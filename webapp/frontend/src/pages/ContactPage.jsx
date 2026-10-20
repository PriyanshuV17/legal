import { useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function ContactPage() {
  const [form, setForm] = useState({ name: "", email: "", subject: "", message: "" });
  const [status, setStatus] = useState("");

  async function submitContact(event) {
    event.preventDefault();
    await api.post("/contact", form);
    setStatus("Message sent successfully.");
    setForm({ name: "", email: "", subject: "", message: "" });
  }

  return (
    <div className="page split-grid">
      <div className="glass-card">
        <SectionHeader
          eyebrow="Contact"
          title="Let’s talk about LegalBuddy"
          description="For support, feedback, collaboration, or product questions."
        />
        <form className="stack" onSubmit={submitContact}>
          <input placeholder="Your name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input placeholder="Your email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input placeholder="Subject" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} />
          <textarea placeholder="Message" rows="6" value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} />
          <button className="primary-button" type="submit">Send Message</button>
          {status && <p className="success-text">{status}</p>}
        </form>
      </div>
      <div className="glass-card">
        <h3>Developer Contact</h3>
        <p>Priyanshu Verma</p>
        <p>priyasnhu.22190503040@cuj.ac.in</p>
        <p>7376021218</p>
        <p>Signature: Priyanshu.Verma17</p>
      </div>
    </div>
  );
}
