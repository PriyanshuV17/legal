import { Link } from "react-router-dom";
import SectionHeader from "../components/SectionHeader";
import StatCard from "../components/StatCard";

export default function HomePage() {
  return (
    <div className="page">
      <section className="hero">
        <div className="hero-copy">
          <span className="eyebrow">AI Legal Platform</span>
          <h1>Professional legal guidance, case search, and history-aware AI in one product.</h1>
          <p>
            LegalBuddy blends a modern legal workspace with AI chat, searchable judgments, law explorer,
            user accounts, admin analytics, and future-ready booking flows.
          </p>
          <div className="hero-actions">
            <Link to="/chat" className="primary-button">Start Chat</Link>
            <Link to="/auth" className="secondary-button">Login / Register</Link>
          </div>
        </div>
        <div className="hero-panel glass-card">
          <SectionHeader
            eyebrow="Why It Feels Different"
            title="Built like a product, not just a demo"
            description="Dark professional base, energetic orange accents, smooth interaction patterns, and clearly separated user, lawyer, and admin journeys."
          />
          <div className="stats-grid">
            <StatCard label="Role Aware" value="3 modes" helper="User, Lawyer, Admin" />
            <StatCard label="Persistence" value="SQL + Vector" helper="Accounts, history, semantic recall" />
            <StatCard label="Coverage" value="Cases + Laws" helper="Search, save, revisit" />
          </div>
        </div>
      </section>

      <section className="content-grid">
        <div className="feature-card">
          <h3>AI Chat Assistant</h3>
          <p>Context-aware legal Q&A with saved chat history and judgment references.</p>
        </div>
        <div className="feature-card">
          <h3>Case Explorer</h3>
          <p>Search judgments by keyword or year, then save them into your workspace.</p>
        </div>
        <div className="feature-card">
          <h3>Law Explorer</h3>
          <p>Browse IPC, BNS, and constitutional sections with bookmark support.</p>
        </div>
        <div className="feature-card">
          <h3>Admin Control</h3>
          <p>See users, bookings, recent activity, and top queries from one dashboard.</p>
        </div>
      </section>
    </div>
  );
}
