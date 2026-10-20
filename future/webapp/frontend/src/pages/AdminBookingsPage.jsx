import { useEffect, useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function AdminBookingsPage() {
  const [bookings, setBookings] = useState([]);

  async function loadBookings() {
    const { data } = await api.get("/admin/bookings");
    setBookings(data.items);
  }

  useEffect(() => {
    loadBookings();
  }, []);

  async function updateStatus(id, status) {
    await api.patch(`/admin/bookings/${id}`, { status });
    loadBookings();
  }

  return (
    <div className="page stack">
      <SectionHeader eyebrow="Admin" title="Booking Management" description="Review and manage consultation requests." />
      <div className="glass-card">
        {bookings.map((item) => (
          <div className="list-row" key={item.id}>
            <div>
              <span>{item.lawyer_name} | {item.case_type}</span>
              <small>{item.date} {item.time_slot} | {item.mode} | {item.status}</small>
            </div>
            <div className="button-row">
              <button className="ghost-button" onClick={() => updateStatus(item.id, "Approved")}>Approve</button>
              <button className="ghost-button" onClick={() => updateStatus(item.id, "Rejected")}>Reject</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
