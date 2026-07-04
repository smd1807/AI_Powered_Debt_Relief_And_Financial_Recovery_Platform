import { useEffect, useState } from "react";
import { listLoans, generateNegotiationStrategy, generateNegotiationEmail } from "../api/client";

export default function Negotiation() {
  const [loans, setLoans] = useState([]);
  const [selectedLoanId, setSelectedLoanId] = useState("");
  const [strategy, setStrategy] = useState(null);
  const [email, setEmail] = useState(null);
  const [error, setError] = useState("");
  const [loadingStrategy, setLoadingStrategy] = useState(false);
  const [loadingEmail, setLoadingEmail] = useState(false);
  const [view, setView] = useState("strategy"); // strategy | letter

  useEffect(() => {
    listLoans().then((d) => {
      setLoans(d);
      if (d.length > 0) setSelectedLoanId(d[0].loan_id);
    });
  }, []);

  const handleStrategy = async () => {
    setLoadingStrategy(true);
    setError("");
    try {
      const res = await generateNegotiationStrategy(selectedLoanId || undefined);
      setStrategy(res);
      setView("strategy");
    } catch {
      setError("Could not generate a strategy right now.");
    } finally {
      setLoadingStrategy(false);
    }
  };

  const handleEmail = async () => {
    if (!selectedLoanId) return;
    setLoadingEmail(true);
    setError("");
    try {
      const res = await generateNegotiationEmail(selectedLoanId);
      setEmail(res);
      setView("letter");
    } catch {
      setError("Could not generate a negotiation letter right now.");
    } finally {
      setLoadingEmail(false);
    }
  };

  return (
    <div className="app-shell">
      <div className="page-header">
        <span className="page-eyebrow">AI Negotiation</span>
        <h1>Negotiation Strategy & Settlement Letter</h1>
        <p>
          The AI drafts a practical negotiation approach and a ready-to-send settlement letter.
          If no live AI provider is configured, a reliable rule-based engine steps in
          automatically — every request is logged to your History page.
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loans.length === 0 ? (
        <div className="card empty-state">
          <h3>No loans to negotiate yet</h3>
          <p>Add a loan on the Loans page first.</p>
        </div>
      ) : (
        <div className="card" style={{ marginBottom: 24 }}>
          <div className="form-grid">
            <div>
              <label>Select a loan</label>
              <select value={selectedLoanId} onChange={(e) => setSelectedLoanId(e.target.value)}>
                {loans.map((l) => (
                  <option key={l.loan_id} value={l.loan_id}>
                    {l.lender_name} — ₹{Number(l.outstanding_amount).toLocaleString("en-IN")}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div style={{ display: "flex", gap: 10 }}>
            <button onClick={handleStrategy} disabled={loadingStrategy}>
              {loadingStrategy ? "Generating..." : "Generate Negotiation Strategy"}
            </button>
            <button className="secondary" onClick={handleEmail} disabled={loadingEmail}>
              {loadingEmail ? "Generating..." : "Generate Settlement Letter"}
            </button>
          </div>
        </div>
      )}

      {(strategy || email) && (
        <div className="card">
          <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
            {strategy && (
              <button
                className={view === "strategy" ? "" : "secondary"}
                onClick={() => setView("strategy")}
              >
                Negotiation Strategy
              </button>
            )}
            {email && (
              <button
                className={view === "letter" ? "" : "secondary"}
                onClick={() => setView("letter")}
              >
                Settlement Letter
              </button>
            )}
          </div>

          <div className="strategy-box">
            {view === "strategy" && strategy ? strategy.negotiation_strategy : null}
            {view === "letter" && email ? email.settlement_letter : null}
          </div>
          <div className="strategy-meta">
            <span>
              SOURCE:{" "}
              {(view === "strategy" ? strategy?.source : email?.source)?.toUpperCase()}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
