import { useEffect, useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function NeedHelpDashboard({ user }) {
  const [bookings, setBookings] = useState([]);
  const [savedCases, setSavedCases] = useState([]);
  const [recommendedLawyers, setRecommendedLawyers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) return;
    
    setLoading(true);
    Promise.all([
      api.get(`/users/${user.id}/saved`).then(res => res.data),
      api.get(`/api/lawyers/recommend?state=${user.state || ""}&city=${user.city || ""}`).then(res => res.data.recommendations || []).catch(() => [])
    ]).then(([saved, lawyers]) => {
      setSavedCases(saved.cases || []);
      setRecommendedLawyers(lawyers.slice(0, 3));
      
      // Mock bookings for demo
      setBookings([
        {
          id: 1,
          lawyer: "Recommended Lawyer",
          date: "Upcoming",
          status: "pending"
        }
      ]);
    }).catch(console.error).finally(() => setLoading(false));
  }, [user?.id, user?.state, user?.city]);

  return (
    <div className="page stack">
      <SectionHeader
        eyebrow="Urgent Support"
        title="Legal Help Dashboard"
        description="Quick access to lawyers, saved cases, and legal resources."
      />

      {/* Quick Stats */}
      <div className="alert-banner glass-card">
        <h3>👋 Welcome, {user?.name || "User"}!</h3>
        <p>Need legal help? We can connect you with qualified lawyers in your area.</p>
      </div>

      {/* Two Main Sections */}
      <div className="two-column-hero">
        {/* Find Lawyer NOW */}
        <section className="glass-card urgent-action">
          <SectionHeader eyebrow="Quick" title="Find a Lawyer Now" />
          <p>Connect with lawyers based on your location, language, and legal needs.</p>
          <a href="/lawyers" className="cta-button">
            🔍 Search Lawyers ({recommendedLawyers.length} Available)
          </a>
          
          {recommendedLawyers.length > 0 && (
            <div className="recommended-list">
              <strong>Recommended for you:</strong>
              <div className="stack compact">
                {recommendedLawyers.map((lawyer, idx) => (
                  <div key={idx} className="lawyer-chip">
                    <span>⭐ {lawyer.name || "Expert Lawyer"}</span>
                    <small>{lawyer.speciality || "Criminal Law"}</small>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* Chat for Guidance */}
        <section className="glass-card urgent-action">
          <SectionHeader eyebrow="Support" title="Ask for Legal Guidance" />
          <p>Describe your legal issue and get immediate guidance from our AI assistant.</p>
          <a href="/chat" className="cta-button">
            💬 Start Chat with LegalBuddy
          </a>
          <p className="hint">Available 24/7 • Free guidance • No judgment</p>
        </section>
      </div>

      {/* Three Column Grid */}
      <div className="three-column">
        {/* Your Bookings */}
        <section className="glass-card">
          <SectionHeader eyebrow="Bookings" title="Consultations" />
          {bookings.length > 0 ? (
            <div className="stack compact">
              {bookings.map((booking) => (
                <div key={booking.id} className="booking-card">
                  <strong>{booking.lawyer}</strong>
                  <small>{booking.date}</small>
                  <span className={`status ${booking.status}`}>{booking.status}</span>
                </div>
              ))}
              <a href="/bookings" className="secondary-button">View All</a>
            </div>
          ) : (
            <div className="placeholder">
              <p>No bookings yet</p>
              <a href="/lawyers">Book a Consultation</a>
            </div>
          )}
        </section>

        {/* Saved Cases */}
        <section className="glass-card">
          <SectionHeader eyebrow="Reference" title="Saved Cases" />
          {savedCases.length > 0 ? (
            <div className="stack compact">
              {savedCases.slice(0, 3).map((case_) => (
                <div key={case_.id} className="case-card">
                  <strong>{case_.title}</strong>
                  <small>{case_.year}</small>
                </div>
              ))}
              {savedCases.length > 3 && (
                <a href="/my-cases" className="secondary-button">
                  View All ({savedCases.length})
                </a>
              )}
            </div>
          ) : (
            <div className="placeholder">
              <p>No saved cases</p>
              <a href="/cases">Explore Cases</a>
            </div>
          )}
        </section>

        {/* Quick Resources */}
        <section className="glass-card">
          <SectionHeader eyebrow="Learn" title="Quick Resources" />
          <div className="stack">
            <a href="/laws" className="resource-link">
              📋 Browse Laws & Sections
            </a>
            <a href="/profile" className="resource-link">
              👤 Update Your Profile
            </a>
            <a href="/contact" className="resource-link">
              📞 Contact Support
            </a>
          </div>
        </section>
      </div>

      {/* Help Sections */}
      <section className="glass-card">
        <SectionHeader eyebrow="Support" title="Common Legal Issues" />
        <div className="issue-grid">
          <div className="issue-card">
            <h4>🚗 Traffic & Vehicle Issues</h4>
            <p>Accidents, licenses, traffic violations</p>
          </div>
          <div className="issue-card">
            <h4>👨‍👩‍👧 Family Matters</h4>
            <p>Marriage, divorce, custody, inheritance</p>
          </div>
          <div className="issue-card">
            <h4>🏠 Property & Housing</h4>
            <p>Disputes, ownership, tenancy</p>
          </div>
          <div className="issue-card">
            <h4>💼 Business & Employment</h4>
            <p>Contracts, disputes, HR issues</p>
          </div>
        </div>
      </section>

      <style>{`
        .alert-banner {
          background: linear-gradient(135deg, #ff9500 0%, #ff6b6b 100%);
          color: white;
          padding: 2rem;
          border-radius: 1rem;
          margin-bottom: 2rem;
        }
        
        .alert-banner h3 {
          margin: 0;
          font-size: 1.5rem;
        }
        
        .two-column-hero {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 2rem;
          margin: 2rem 0;
        }
        
        .urgent-action {
          padding: 2rem;
          border: 2px solid #ff9500;
          position: relative;
        }
        
        .cta-button {
          display: block;
          padding: 1rem;
          background: linear-gradient(135deg, #ff9500 0%, #ff6b6b 100%);
          color: white;
          border-radius: 0.5rem;
          text-align: center;
          text-decoration: none;
          font-weight: bold;
          margin: 1rem 0;
          transition: transform 0.2s;
        }
        
        .cta-button:hover {
          transform: scale(1.05);
        }
        
        .hint {
          font-size: 0.85rem;
          color: #666;
          margin-top: 0.5rem;
        }
        
        .recommended-list {
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid rgba(0, 0, 0, 0.1);
        }
        
        .lawyer-chip {
          display: block;
          padding: 0.75rem;
          background: rgba(255, 149, 0, 0.05);
          border-left: 3px solid #ff9500;
          margin: 0.5rem 0;
          border-radius: 0.25rem;
        }
        
        .three-column {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 2rem;
          margin: 2rem 0;
        }
        
        .booking-card, .case-card {
          padding: 1rem;
          background: rgba(255, 149, 0, 0.05);
          border-radius: 0.5rem;
          border-left: 3px solid #ff9500;
        }
        
        .status {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          background: #ff9500;
          color: white;
          border-radius: 1rem;
          font-size: 0.75rem;
          margin-top: 0.5rem;
        }
        
        .placeholder {
          text-align: center;
          padding: 1rem;
          color: #999;
        }
        
        .placeholder a {
          display: block;
          margin-top: 0.5rem;
          color: #ff9500;
          text-decoration: none;
        }
        
        .resource-link {
          display: block;
          padding: 0.75rem;
          background: rgba(255, 149, 0, 0.1);
          border-radius: 0.5rem;
          text-decoration: none;
          margin: 0.5rem 0;
          transition: all 0.2s;
        }
        
        .resource-link:hover {
          background: rgba(255, 149, 0, 0.2);
          transform: translateX(0.25rem);
        }
        
        .issue-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1.5rem;
          margin-top: 1rem;
        }
        
        .issue-card {
          padding: 1.5rem;
          background: rgba(255, 149, 0, 0.05);
          border-radius: 0.75rem;
          border-left: 4px solid #ff9500;
        }
        
        .issue-card h4 {
          margin: 0 0 0.5rem 0;
          color: #ff9500;
        }
        
        .issue-card p {
          margin: 0;
          font-size: 0.9rem;
          color: #666;
        }
        
        @media (max-width: 1024px) {
          .three-column {
            grid-template-columns: 1fr 1fr;
          }
        }
        
        @media (max-width: 768px) {
          .two-column-hero {
            grid-template-columns: 1fr;
          }
          
          .three-column {
            grid-template-columns: 1fr;
          }
          
          .issue-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}
