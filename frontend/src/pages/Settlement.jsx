import { useEffect, useState } from "react";
import { listLoans, predictSettlement } from "../api/client";
import { RiskBadge } from "../components/StatCard";

export default function Settlement() {
  const [loans, setLoans] = useState([]);
  const [selectedLoanId, setSelectedLoanId] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    listLoans().then((d) => {
      setLoans(d);
      if (d.length > 0) setSelectedLoanId(d[0].loan_id);
    });
  }, []);

  const handlePredict = async () => {
    if (!selectedLoanId) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await predictSettlement(selectedLoanId);
      setResult(res[0]);
    } catch {
      setError("Prediction failed. Please try again in a moment.");
    } finally {
      setLoading(false);
    }
  };

  const inr = (n) => `₹${Number(n).toLocaleString("en-IN")}`;

  return (
    <div className="app-shell">
      <div className="page-header">
        <span className="page-eyebrow">Settlement Predictor</span>
        <h1>What Might a Lender Actually Accept?</h1>
        <p>
          The model estimates a realistic full-and-final settlement based on overdue months,
          interest rate, EMI burden, and your overall debt-to-income ratio — and flags a risk
          level for how urgently to act.
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loans.length === 0 ? (
        <div className="card empty-state">
          <h3>No loans to analyze</h3>
          <p>Add a loan on the Loans page first.</p>
        </div>
      ) : (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="form-grid" style={{ alignItems: "end" }}>
            <div>
              <label>Select a loan</label>
              <select value={selectedLoanId} onChange={(e) => setSelectedLoanId(e.target.value)}>
                {loans.map((l) => (
                  <option key={l.loan_id} value={l.loan_id}>
                    {l.lender_name} — {inr(l.outstanding_amount)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <button onClick={handlePredict} disabled={loading}>
                {loading ? "Predicting..." : "Run settlement prediction"}
              </button>
            </div>
          </div>
        </div>
      )}

      {result && (
        <div className="card">
          <div className="section-title">Prediction for {result.lender_name}</div>
          <div className="card-grid" style={{ marginBottom: 0 }}>
            <div className="stat-card">
              <div className="stat-label">Suggested Settlement</div>
              <div className="stat-value mono">{result.suggested_settlement_percentage}%</div>
              <div className="stat-sub">
                ≈ {inr((result.outstanding_amount * result.suggested_settlement_percentage) / 100)}
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Risk Category</div>
              <div style={{ marginTop: 6 }}>
                <RiskBadge level={result.risk_category} />
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Outstanding Amount</div>
              <div className="stat-value mono">{inr(result.outstanding_amount)}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Monthly EMI</div>
              <div className="stat-value mono">{inr(result.emi)}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
