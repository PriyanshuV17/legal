export default function BrandMark({ watermark = false }) {
  return (
    <div className={`brandmark ${watermark ? "brandmark-watermark" : ""}`}>
      <div className="brandmark-badge">LB</div>
      <div>
        <div className="brandmark-title">LegalBuddy AI</div>
        <div className="brandmark-subtitle">Modern Indian Legal Intelligence</div>
      </div>
    </div>
  );
}
