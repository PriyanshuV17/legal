import { useEffect, useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

const initialForm = {
  content_type: "law",
  title: "",
  section_code: "",
  year: "",
  file_name: "",
  description: ""
};

export default function AdminContentPage() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(initialForm);

  async function loadContent() {
    const { data } = await api.get("/admin/content");
    setItems(data.items);
  }

  useEffect(() => {
    loadContent();
  }, []);

  async function createContent(event) {
    event.preventDefault();
    await api.post("/admin/content", form);
    setForm(initialForm);
    loadContent();
  }

  return (
    <div className="page split-grid">
      <div className="glass-card">
        <SectionHeader eyebrow="Admin" title="Content Management" description="Add and update law or case metadata shown in the product UI." />
        <form className="stack" onSubmit={createContent}>
          <select value={form.content_type} onChange={(e) => setForm({ ...form, content_type: e.target.value })}>
            <option value="law">Law</option>
            <option value="case">Case</option>
          </select>
          <input placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <div className="form-row">
            <input placeholder="Section code" value={form.section_code} onChange={(e) => setForm({ ...form, section_code: e.target.value })} />
            <input placeholder="Year" value={form.year} onChange={(e) => setForm({ ...form, year: e.target.value })} />
          </div>
          <input placeholder="File name (for cases)" value={form.file_name} onChange={(e) => setForm({ ...form, file_name: e.target.value })} />
          <textarea rows="4" placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <button className="primary-button" type="submit">Add Content</button>
        </form>
      </div>
      <div className="glass-card">
        <h3>Current Content</h3>
        {items.map((item) => (
          <div className="list-row" key={item.id}>
            <div>
              <span>{item.title}</span>
              <small>{item.content_type} {item.section_code || item.year || ""}</small>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
