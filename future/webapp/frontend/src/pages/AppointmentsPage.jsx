import { useEffect, useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function AppointmentsPage({ user }) {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [filter, setFilter] = useState("all"); // all, upcoming, past

  async function loadAppointments() {
    if (!user?.id) return;
    setLoading(true);
    try {
      const { data } = await api.get(`/appointments/user/${user.id}`);
      setAppointments(data.appointments || []);
    } catch (error) {
      setMessage("Error loading appointments");
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  async function rescheduleAppointment(appointmentId, appointment) {
    const newDate = window.prompt("Enter new date (YYYY-MM-DD):", appointment.date);
    if (!newDate) return;
    
    const newTime = window.prompt("Enter new time (HH:MM):", appointment.time_slot);
    if (!newTime) return;
    
    try {
      await api.patch(`/appointments/${appointmentId}/reschedule`, {
        new_date: newDate,
        new_time: newTime,
        user_id: user.id
      });
      setMessage("✓ Appointment rescheduled successfully");
      loadAppointments();
    } catch (error) {
      setMessage(`Error rescheduling: ${error.message}`);
    }
  }

  async function cancelAppointment(appointmentId) {
    if (!window.confirm("Are you sure you want to cancel this appointment?")) return;
    
    try {
      await api.patch(`/bookings/${appointmentId}/cancel`, { user_id: user.id });
      setMessage("✓ Appointment cancelled successfully");
      loadAppointments();
    } catch (error) {
      setMessage(`Error cancelling: ${error.message}`);
    }
  }

  useEffect(() => {
    loadAppointments();
  }, [user?.id]);

  const isUpcoming = (dateStr) => new Date(dateStr) >= new Date();
  
  const filteredAppointments = appointments.filter(apt => {
    if (filter === "upcoming") return isUpcoming(apt.date);
    if (filter === "past") return !isUpcoming(apt.date);
    return true;
  });

  const getStatusColor = (dateStr) => {
    return isUpcoming(dateStr) ? "#4CAF50" : "#999";
  };

  return (
    <div className="page stack">
      <SectionHeader 
        eyebrow="My Calendar" 
        title="Confirmed Appointments" 
        description="View your scheduled consultations with lawyers." 
      />

      <div className="toolbar">
        <button 
          className={filter === "all" ? "primary-button" : "secondary-button"}
          onClick={() => setFilter("all")}
        >
          All ({appointments.length})
        </button>
        <button 
          className={filter === "upcoming" ? "primary-button" : "secondary-button"}
          onClick={() => setFilter("upcoming")}
        >
          Upcoming ({appointments.filter(a => isUpcoming(a.date)).length})
        </button>
        <button 
          className={filter === "past" ? "primary-button" : "secondary-button"}
          onClick={() => setFilter("past")}
        >
          Past ({appointments.filter(a => !isUpcoming(a.date)).length})
        </button>
      </div>

      {message && (
        <p className={message.includes("Error") ? "error-text" : "success-text"}>
          {message}
        </p>
      )}

      {loading && <p>Loading appointments...</p>}

      {!loading && filteredAppointments.length === 0 && (
        <div className="glass-card">
          <p>
            {filter === "all" && "No appointments scheduled yet. "}
            {filter === "upcoming" && "No upcoming appointments. "}
            {filter === "past" && "No past appointments. "}
            <a href="/booking">Book a lawyer</a> to schedule a consultation.
          </p>
        </div>
      )}

      <div className="appointments-list">
        {filteredAppointments.map((apt) => {
          const appointmentDate = new Date(apt.date);
          const isUpcomingApt = isUpcoming(apt.date);
          
          return (
            <div key={apt.id} className="glass-card appointment-card">
              <div className="appointment-header">
                <div>
                  <h3>{apt.lawyer_name}</h3>
                  <p className="text-muted">{apt.case_type}</p>
                </div>
                <span 
                  className="status-badge" 
                  style={{ 
                    backgroundColor: getStatusColor(apt.date),
                    color: "white",
                    padding: "4px 12px",
                    borderRadius: "12px",
                    fontSize: "12px",
                    fontWeight: "bold"
                  }}
                >
                  {isUpcomingApt ? "Upcoming" : "Completed"}
                </span>
              </div>

              <div className="appointment-calendar">
                <div className="calendar-date">
                  <div className="day">{appointmentDate.getDate()}</div>
                  <div className="month">{appointmentDate.toLocaleString('default', { month: 'short' })}</div>
                  <div className="year">{appointmentDate.getFullYear()}</div>
                </div>
                <div className="appointment-time">
                  <div>
                    <strong>Time:</strong> {apt.time_slot}
                  </div>
                  <div>
                    <strong>Mode:</strong> {apt.mode}
                  </div>
                  {apt.notes && (
                    <div>
                      <strong>Notes:</strong> {apt.notes}
                    </div>
                  )}
                </div>
              </div>

              {isUpcomingApt && (
                <div className="appointment-actions">
                  <button 
                    className="secondary-button"
                    onClick={() => rescheduleAppointment(apt.id, apt)}
                  >
                    Reschedule
                  </button>
                  <button 
                    className="danger-button"
                    onClick={() => cancelAppointment(apt.id)}
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <style>{`
        .appointments-list {
          display: grid;
          gap: 1.5rem;
          margin-top: 1.5rem;
        }

        .appointment-card {
          padding: 1.5rem;
        }

        .appointment-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 1.5rem;
          border-bottom: 1px solid rgba(255,255,255,0.1);
          padding-bottom: 1rem;
        }

        .appointment-calendar {
          display: flex;
          gap: 2rem;
          align-items: center;
          margin: 1.5rem 0;
          padding: 1rem;
          background: rgba(255,255,255,0.05);
          border-radius: 8px;
        }

        .calendar-date {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 8px;
          padding: 1rem;
          text-align: center;
          min-width: 80px;
          color: white;
        }

        .calendar-date .day {
          font-size: 2rem;
          font-weight: bold;
        }

        .calendar-date .month {
          font-size: 0.9rem;
          text-transform: uppercase;
        }

        .calendar-date .year {
          font-size: 0.8rem;
          opacity: 0.8;
        }

        .appointment-time {
          flex: 1;
        }

        .appointment-time div {
          margin: 0.5rem 0;
        }

        .appointment-actions {
          display: flex;
          gap: 1rem;
          margin-top: 1.5rem;
          padding-top: 1rem;
          border-top: 1px solid rgba(255,255,255,0.1);
        }

        .appointment-actions button {
          flex: 1;
        }
      `}</style>
    </div>
  );
}
