export default function StatCard({ label, value, sub, mono = true }) {
  return (
    <div className="card stat-card">
      <div className="stat-label">{label}</div>
      <div className={`stat-value ${mono ? "mono" : ""}`}>{value}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}

export function HealthBadge({ category }) {
  const slug = category.toLowerCase().replace(/\s+/g, "-");
  return <span className={`badge badge-${slug}`}>{category}</span>;
}

export function RiskBadge({ level }) {
  const slug = level.toLowerCase();
  return <span className={`badge badge-${slug}`}>{level}</span>;
}
