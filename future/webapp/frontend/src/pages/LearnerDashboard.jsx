import { useEffect, useState } from "react";
import { api } from "../api";
import SectionHeader from "../components/SectionHeader";

export default function LearnerDashboard({ user }) {
  const [history, setHistory] = useState([]);
  const [savedLaws, setSavedLaws] = useState([]);
  const [stats, setStats] = useState({
    questionsAsked: 0,
    lawsSaved: 0,
    casesSaved: 0,
    topicsLearned: []
  });

  useEffect(() => {
    if (!user?.id) return;
    
    Promise.all([
      api.get(`/users/${user.id}/history`),
      api.get(`/users/${user.id}/saved`)
    ]).then(([historyRes, savedRes]) => {
      const sessions = historyRes.data.sessions || [];
      const saved = savedRes.data;
      
      setHistory(sessions);
      setSavedLaws(saved.laws || []);
      
      setStats({
        questionsAsked: sessions.reduce((sum, s) => sum + (s.message_count || 0), 0),
        lawsSaved: (saved.laws || []).length,
        casesSaved: (saved.cases || []).length,
        topicsLearned: sessions.slice(0, 5).map(s => s.title)
      });
    }).catch(console.error);
  }, [user?.id]);

  return (
    <div className="page stack">
      <SectionHeader
        eyebrow="Learning Mode"
        title="Your Learning Dashboard"
        description="Track your legal education journey and saved resources."
      />

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card glass-card">
          <h3>Questions Asked</h3>
          <p className="stat-value">{stats.questionsAsked}</p>
          <small>Keep exploring to learn more!</small>
        </div>
        <div className="stat-card glass-card">
          <h3>Laws Saved</h3>
          <p className="stat-value">{stats.lawsSaved}</p>
          <small>Quick reference resources</small>
        </div>
        <div className="stat-card glass-card">
          <h3>Cases Saved</h3>
          <p className="stat-value">{stats.casesSaved}</p>
          <small>Landmark judgments to study</small>
        </div>
        <div className="stat-card glass-card">
          <h3>Topics Explored</h3>
          <p className="stat-value">{stats.topicsLearned.length}</p>
          <small>Different areas of law</small>
        </div>
      </div>

      <div className="two-column">
        {/* Recent Topics */}
        <section className="glass-card">
          <SectionHeader eyebrow="Recent" title="Topics Explored" />
          <div className="stack compact">
            {stats.topicsLearned.length > 0 ? (
              stats.topicsLearned.map((topic, idx) => (
                <div key={idx} className="topic-item">
                  <strong>{topic}</strong>
                  <small>View related laws & cases</small>
                </div>
              ))
            ) : (
              <p className="placeholder">Start asking questions to explore topics!</p>
            )}
          </div>
        </section>

        {/* Quick Actions */}
        <section className="glass-card">
          <SectionHeader eyebrow="Action" title="What's Next?" />
          <div className="stack">
            <a href="/chat" className="action-button">
              📚 Ask Legal Questions
            </a>
            <a href="/laws" className="action-button">
              ⚖️ Browse Indian Laws
            </a>
            <a href="/cases" className="action-button">
              📖 Study Cases
            </a>
            <a href="/profile" className="action-button">
              👤 Update Profile
            </a>
          </div>
        </section>
      </div>

      {/* Saved Laws Reference */}
      {savedLaws.length > 0 && (
        <section className="glass-card">
          <SectionHeader eyebrow="Bookmarks" title="Your Saved Laws" />
          <div className="stack compact">
            {savedLaws.map((law) => (
              <div key={law.id} className="saved-item">
                <strong>{law.title}</strong>
                <code>{law.section_code}</code>
                <small>{law.description}</small>
              </div>
            ))}
          </div>
        </section>
      )}

      <style>{`
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1.5rem;
          margin: 2rem 0;
        }
        
        .stat-card {
          padding: 2rem;
          text-align: center;
        }
        
        .stat-value {
          font-size: 2.5rem;
          font-weight: bold;
          color: #ff9500;
          margin: 0.5rem 0;
        }
        
        .two-column {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 2rem;
          margin: 2rem 0;
        }
        
        .topic-item, .saved-item {
          padding: 1rem;
          border-left: 3px solid #ff9500;
          background: rgba(255, 149, 0, 0.05);
          border-radius: 0.5rem;
        }
        
        .action-button {
          display: block;
          padding: 1rem;
          background: rgba(255, 149, 0, 0.1);
          border: 1px solid #ff9500;
          border-radius: 0.5rem;
          text-decoration: none;
          transition: all 0.2s;
          text-align: center;
        }
        
        .action-button:hover {
          background: rgba(255, 149, 0, 0.2);
          transform: translateX(0.25rem);
        }
        
        @media (max-width: 768px) {
          .two-column {
            grid-template-columns: 1fr;
          }
          
          .stats-grid {
            grid-template-columns: 1fr 1fr;
          }
        }
      `}</style>
    </div>
  );
}
