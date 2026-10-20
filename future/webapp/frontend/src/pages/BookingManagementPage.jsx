import { useEffect, useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function BookingManagementPage({ user }) {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  async function loadBookings() {
    if (!user?.id) return;
    setLoading(true);
    try {
      const { data } = await api.get(`/bookings/user/${user.id}`);
      setBookings(data.bookings || []);
    } catch (error) {
      setMessage("Error loading bookings");
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  async function cancelBooking(bookingId) {
    if (!window.confirm("Are you sure you want to cancel this booking?")) return;
    
    try {
      await api.patch(`/bookings/${bookingId}/cancel`, { user_id: user.id });
      setMessage("✓ Booking cancelled successfully");
      loadBookings();
    } catch (error) {
      setMessage(`Error cancelling booking: ${error.message}`);
    }
  }

  async function rescheduleBooking(bookingId, booking) {
    const newDate = window.prompt("Enter new date (YYYY-MM-DD):", booking.date);
    if (!newDate) return;
    
    const newTime = window.prompt("Enter new time (HH:MM):", booking.time_slot);
    if (!newTime) return;
    
    try {
      await api.patch(`/appointments/${bookingId}/reschedule`, {
        new_date: newDate,
        new_time: newTime,
        user_id: user.id
      });
      setMessage("✓ Appointment rescheduled successfully");
      loadBookings();
    } catch (error) {
      setMessage(`Error rescheduling: ${error.message}`);
    }
  }

  useEffect(() => {
    loadBookings();
  }, [user?.id]);

  const statusColors = {
    "Pending": "#ffa500",
    "Confirmed": "#4CAF50",
    "Cancelled": "#f44336"
  };

  return (
    <div className="page stack">
      <SectionHeader 
        eyebrow="My Bookings" 
        title="Booking Management" 
        description="View, manage, and reschedule your lawyer consultations." 
      />

      {message && (
        <p className={message.includes("Error") ? "error-text" : "success-text"}>
          {message}
        </p>
      )}

      {loading && <p>Loading bookings...</p>}

      {!loading && bookings.length === 0 && (
        <div className="glass-card">
          <p>No bookings yet. <a href="/booking">Book a lawyer</a> to get started.</p>
        </div>
      )}

      <div className="content-grid">
        {bookings.map((booking) => (
          <div key={booking.id} className="glass-card booking-card">
            <div className="booking-header">
              <h3>{booking.lawyer_name}</h3>
              <span 
                className="status-badge" 
                style={{ 
                  backgroundColor: statusColors[booking.status] || "#999",
                  color: "white",
                  padding: "4px 12px",
                  borderRadius: "12px",
                  fontSize: "12px",
                  fontWeight: "bold"
                }}
              >
                {booking.status}
              </span>
            </div>

            <div className="booking-details">
              <div><strong>Case Type:</strong> {booking.case_type}</div>
              <div><strong>Mode:</strong> {booking.mode}</div>
              <div><strong>Date:</strong> {booking.date}</div>
              <div><strong>Time:</strong> {booking.time_slot}</div>
              {booking.notes && <div><strong>Notes:</strong> {booking.notes}</div>}
              <div className="text-muted"><small>Created: {new Date(booking.created_at).toLocaleDateString()}</small></div>
            </div>

            <div className="booking-actions">
              {booking.status === "Pending" && (
                <>
                  <button 
                    className="secondary-button"
                    onClick={() => rescheduleBooking(booking.id, booking)}
                  >
                    Reschedule
                  </button>
                  <button 
                    className="danger-button"
                    onClick={() => cancelBooking(booking.id)}
                  >
                    Cancel
                  </button>
                </>
              )}
              {booking.status === "Confirmed" && (
                <>
                  <button 
                    className="secondary-button"
                    onClick={() => rescheduleBooking(booking.id, booking)}
                  >
                    Reschedule
                  </button>
                  <button 
                    className="danger-button"
                    onClick={() => cancelBooking(booking.id)}
                  >
                    Cancel
                  </button>
                </>
              )}
              {booking.status === "Cancelled" && (
                <p className="text-muted">This booking has been cancelled.</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
