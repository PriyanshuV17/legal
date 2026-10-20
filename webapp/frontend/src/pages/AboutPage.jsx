import SectionHeader from "../components/SectionHeader";

export default function AboutPage() {
  return (
    <div className="page stack">
      <SectionHeader
        eyebrow="About LegalBuddy"
        title="An accessible AI layer for Indian legal workflows"
        description="Built to make legal information easier to navigate for learners, citizens, and professionals."
      />
      <div className="split-grid">
        <div className="glass-card">
          <h3>Vision</h3>
          <p>Bring legal guidance, case intelligence, and operational dashboards into one calm, reliable workspace.</p>
        </div>
        <div className="glass-card">
          <h3>How AI Works</h3>
          <p>The platform retrieves relevant legal materials, combines them with role-aware prompting, and stores useful history for later retrieval.</p>
        </div>
        <div className="glass-card">
          <h3>Disclaimer</h3>
          <p>LegalBuddy supports legal understanding and workflow assistance. It is not a substitute for licensed legal representation.</p>
        </div>
      </div>
    </div>
  );
}
