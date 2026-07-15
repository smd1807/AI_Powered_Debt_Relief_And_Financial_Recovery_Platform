import { useEffect, useState } from "react";
import { getDashboardData, updateProfile } from "../api/client";
import { useAuth } from "../api/AuthContext";
import StatCard, { HealthBadge } from "../components/StatCard";
import { HealthGauge, DebtBreakdownChart } from "../components/Charts";

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [income, setIncome] = useState("");
  const [expenses, setExpenses] = useState("");
  const [lumpSum, setLumpSum] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoading(true);
    getDashboardData()
      .then((d) => {
        setData(d);
        setIncome(d.monthly_income || "");
        setExpenses(d.monthly_expenses || "");
        setLumpSum(d.lump_sum_available || "");
        if (!d.profile_id) setShowForm(true);
      })
      .catch(() => setError("Could not load your dashboard right now."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const updated = await updateProfile({
        monthly_income: Number(income),
        monthly_expenses: Number(expenses) || 0,
        lump_sum_available: Number(lumpSum) || 0,
      });
      setData(updated);
      setShowForm(false);
    } catch {
      setError("Could not save your financial profile.");
    } finally {
      setSaving(false);
    }
  };

  const inr = (n) => `₹${Number(n).toLocaleString("en-IN")}`;

  if (loading) return <div className="app-shell loading-text">Loading your dashboard…</div>;

  return (
    <div className="app-shell">
      <div className="page-header">
        <span className="page-eyebrow">Overview</span>
        <h1>Welcome back{user ? `, ${user.name.split(" ")[0]}` : ""}</h1>
        <p>
          A live snapshot of where you stand — debt load, disposable income, and the health
          score the AI uses to plan settlement and negotiation strategy.
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {(showForm || !data?.profile_id) && (
        <form className="card" onSubmit={handleSave} style={{ marginBottom: 24 }}>
          <div className="section-title">
            {data?.profile_id ? "Update your financial details" : "Set up your financial profile"}
          </div>
          <div className="form-grid">
            <div>
              <label>Monthly income (₹)</label>
              <input type="number" value={income} onChange={(e) => setIncome(e.target.value)} required min="0" />
            </div>
            <div>
              <label>Monthly expenses (₹)</label>
              <input type="number" value={expenses} onChange={(e) => setExpenses(e.target.value)} min="0" />
            </div>
            <div>
              <label>Lump sum available (₹)</label>
              <input type="number" value={lumpSum} onChange={(e) => setLumpSum(e.target.value)} min="0" />
            </div>
          </div>
          <button type="submit" disabled={saving}>
            {saving ? "Saving..." : "Save & calculate"}
          </button>
        </form>
      )}

      {data && data.profile_id > 0 && !showForm && (
        <>
          <div className="card-grid">
            <div className="card stat-card">
              <div className="stat-label">Health Score</div>
              <HealthGauge score={data.financial_health_score} />
              <div style={{ textAlign: "center" }}>
                <HealthBadge category={data.health_category} />
              </div>
            </div>
            <StatCard
              label="Total Outstanding Debt"
              value={inr(data.existing_debts)}
              sub={`${data.loans.length} active loan${data.loans.length === 1 ? "" : "s"}`}
            />
            <StatCard
              label="Debt-to-Income Ratio"
              value={`${data.debt_to_income_ratio}%`}
              sub="Estimated monthly obligation vs income"
            />
            <StatCard
              label="Monthly Surplus"
              value={inr(data.disposable_income)}
              sub="After expenses & estimated obligations"
            />
          </div>

          {data.loans.length > 0 ? (
            <div className="card">
              <div className="section-title">Outstanding Debt by Lender</div>
              <DebtBreakdownChart loans={data.loans} />
            </div>
          ) : (
            <div className="card empty-state">
              <h3>No active loans recorded yet</h3>
              <p>Head to the Loans tab to add your first one.</p>
            </div>
          )}

          <button className="secondary" style={{ marginTop: 20 }} onClick={() => setShowForm(true)}>
            Update financial details
          </button>
        </>
      )}
    </div>
  );
}
