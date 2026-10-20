import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function BookingPage({ user }) {
  const [searchParams] = useSearchParams();
  const [form, setForm] = useState({
    lawyer_id: 0,
    lawyer_name: searchParams.get("lawyer") || "Select a lawyer",
    case_description: "",
    consultation_type: "Online",
    preferred_date: "",
    preferred_time: "",
    notes: ""
  });
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!user) return;
    setForm(prev => ({ ...prev, lawyer_name: searchParams.get("lawyer") || prev.lawyer_name }));
  }, [searchParams, user]);

  async function submitBooking(event) {
    event.preventDefault();
    
    if (!form.case_description.trim()) {
      setMessage("Please describe your case");
      return;
    }
    if (!form.preferred_date) {
      setMessage("Please select a preferred date");
      return;
    }
    if (!form.preferred_time) {
      setMessage("Please select a preferred time");
      return;
    }

    setLoading(true);
    setMessage("");
    setSuccess(false);

    try {
      const { data } = await api.post("/bookings/create", {
        lawyer_id: form.lawyer_id || 1,
        case_description: form.case_description,
        preferred_date: form.preferred_date,
        preferred_time: form.preferred_time,
        consultation_type: form.consultation_type,
        notes: form.notes,
        user_id: user.id
      });
      
      setSuccess(true);
      setMessage(`✓ Booking created successfully! Booking ID: ${data.booking_id}`);
      setForm({
        lawyer_id: 0,
        lawyer_name: "Select a lawyer",
        case_description: "",
        consultation_type: "Online",
        preferred_date: "",
        preferred_time: "",
        notes: ""
      });
      
      setTimeout(() => {
        window.location.href = `/bookings`;
      }, 2000);
    } catch (error) {
      setMessage(`Error creating booking: ${error.message}`);
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page split-grid">
      <div className="glass-card">
        <SectionHeader 
          eyebrow="Book a Lawyer" 
          title="Schedule a Consultation" 
          description="Book a lawyer consultation with your preferred date, time, and mode of consultation." 
        />
        <form className="stack" onSubmit={submitBooking}>
          <div>
            <label>Lawyer Name</label>
            <input 
              type="text"
              value={form.lawyer_name} 
              onChange={(e) => setForm({ ...form, lawyer_name: e.target.value })} 
              placeholder="Lawyer name" 
              required
            />
          </div>

          <div>
            <label>Case Description</label>
            <textarea 
              rows="4"
              value={form.case_description}
              onChange={(e) => setForm({ ...form, case_description: e.target.value })}
              placeholder="Describe your case/legal issue"
              required
            />
          </div>

          <div className="form-row">
            <div>
              <label>Consultation Mode</label>
              <select 
                value={form.consultation_type} 
                onChange={(e) => setForm({ ...form, consultation_type: e.target.value })}
              >
                <option>Online</option>
                <option>Offline</option>
                <option>Hybrid</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div>
              <label>Preferred Date</label>
              <input 
                type="date" 
                value={form.preferred_date} 
                onChange={(e) => setForm({ ...form, preferred_date: e.target.value })} 
                required
              />
            </div>
            <div>
              <label>Preferred Time</label>
              <input 
                type="time" 
                value={form.preferred_time} 
                onChange={(e) => setForm({ ...form, preferred_time: e.target.value })} 
                required
              />
            </div>
          </div>

          <div>
            <label>Additional Notes</label>
            <textarea 
              rows="3" 
              placeholder="Any additional information or questions for the lawyer" 
              value={form.notes} 
              onChange={(e) => setForm({ ...form, notes: e.target.value })} 
            />
          </div>

          <button 
            className="primary-button" 
            type="submit"
            disabled={loading}
          >
            {loading ? "Booking..." : "Book Consultation"}
          </button>

          {message && (
            <p className={success ? "success-text" : "error-text"}>
              {message}
            </p>
          )}
        </form>
      </div>

      <div className="glass-card">
        <SectionHeader eyebrow="Booking Info" title="What Happens Next" />
        <div className="stack compact">
          <div>
            <h4>✓ Booking Details Saved</h4>
            <p>Your booking request is recorded in our system.</p>
          </div>
          <div>
            <h4>📞 Lawyer Contact</h4>
            <p>The lawyer will contact you to confirm the consultation date and time.</p>
          </div>
          <div>
            <h4>💬 Consultation</h4>
            <p>Consult with your lawyer on the confirmed date/time via your preferred mode.</p>
          </div>
          <div>
            <h4>📋 Record Keeping</h4>
            <p>View and manage all your bookings from the My Bookings page.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
