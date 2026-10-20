import SectionHeader from "../components/SectionHeader";

export default function LawyerHubPage() {
  return (
    <div className="page stack">
      <SectionHeader
        eyebrow="Future Lawyer Panel"
        title="Lawyer Dashboard"
        description="Reserved for assigned cases, appointment management, and client communication."
      />
      <div className="content-grid">
        <div className="glass-card">
          <h3>Assigned Cases</h3>
          <p>Design placeholder for future request routing and case assignment workflows.</p>
        </div>
        <div className="glass-card">
          <h3>Appointment Management</h3>
          <p>Accept, reject, and manage calendar slots from user bookings.</p>
        </div>
        <div className="glass-card">
          <h3>Client Communication</h3>
          <p>Secure chat and document exchange can land here in the next phase.</p>
        </div>
      </div>
    </div>
  );
}
