import { useEffect, useState } from "react";
import { getFinancialHealth, getDebtTimeline } from "../api/client";
import { HealthBadge } from "../components/StatCard";
import { DebtTimelineChart } from "../components/Charts";

export default function FinancialHealth() {
  const [health, setHealth] = useState(null);
  const [timeline, setTimeline] = useState(null);
  const [extraPayment, setExtraPayment] = useState("0");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const loadHealth = () => {
    getFinancialHealth()
      .then(setHealth)
      .catch(() => setError("Could not load your financial health right now."));
  };

  const loadTimeline = (extra = 0) => {
    getDebtTimeline(extra)
      .then(setTimeline)
      .catch(() => {});
  };

  useEffect(() => {
    setLoading(true);
    Promise.all([loadHealth(), loadTimeline(0)]).finally(() => setLoading(false));
  }, []);

  const handleSimulate = (e) => {
    e.preventDefault();
    loadTimeline(Number(extraPayment) || 0);
  };

  const inr = (n) => `₹${Number(n).toLocaleString("en-IN")}`;

  if (loading) return <div className="app-shell loading-text">Loading financial health…</div>;

  return (
    <div className="app-shell">
      <div className="page-header">
        <span className="page-eyebrow">Financial Health</span>
        <h1>Your Financial Health & Debt Timeline</h1>
        <p>
          A detailed look at your EMI ratio, debt-to-income ratio, and a simulation of how fast
          you could become debt-free — with or without extra monthly payments.
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {health && (
        <div className="card-grid">
          <div className="card stat-card">
            <div className="stat-label">Health Score</div>
            <div className="stat-value mono">{health.financial_health_score}</div>
            <div style={{ marginTop: 10 }}>
              <HealthBadge category={health.health_category} />
            </div>
          </div>
          <div className="card stat-card">
            <div className="stat-label">Debt-to-Income Ratio</div>
            <div className="stat-value mono">{health.debt_to_income_ratio}%</div>
          </div>
          <div className="card stat-card">
            <div className="stat-label">Monthly Surplus</div>
            <div className="stat-value mono">{inr(health.disposable_income)}</div>
          </div>
          <div className="card stat-card">
            <div className="stat-label">Total Outstanding</div>
            <div className="stat-value mono">{inr(health.existing_debts)}</div>
          </div>
        </div>
      )}

      <div className="card" style={{ marginBottom: 24 }}>
        <div className="section-title">Debt Repayment Timeline</div>
        <form onSubmit={handleSimulate} className="form-grid" style={{ alignItems: "end" }}>
          <div>
            <label>Extra monthly payment (₹, optional)</label>
            <input
              type="number"
              value={extraPayment}
              onChange={(e) => setExtraPayment(e.target.value)}
              min="0"
            />
          </div>
          <div>
            <button type="submit">Simulate payoff</button>
          </div>
        </form>

        {timeline && (
          <>
            <div className="card-grid" style={{ marginTop: 16, marginBottom: 8 }}>
              <StatInline label="Months to Debt-Free" value={timeline.months_to_debt_free} />
              <StatInline
                label="Final Remaining Balance"
                value={inr(timeline.final_remaining_balance)}
              />
            </div>
            {timeline.timeline_preview.length > 0 ? (
              <DebtTimelineChart timeline={timeline.timeline_preview} />
            ) : (
              <div className="empty-state">
                <h3>No active loans to simulate</h3>
                <p>Add a loan on the Loans page first.</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function StatInline({ label, value }) {
  return (
    <div className="card stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value mono" style={{ fontSize: 20 }}>
        {value}
      </div>
    </div>
  );
}
