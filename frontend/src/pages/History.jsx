import { useEffect, useState } from "react";
import { getAIHistory } from "../api/client";

export default function History() {
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    getAIHistory()
      .then(setHistory)
      .catch(() => setError("Could not load your AI history right now."))
      .finally(() => setLoading(false));
  }, []);

  const toggle = (id) => setExpandedId(expandedId === id ? null : id);

  return (
    <div className="app-shell">
      <div className="page-header">
        <span className="page-eyebrow">History</span>
        <h1>Review Past AI Outputs</h1>
        <p>
          Every negotiation strategy and settlement letter the AI has generated for you, kept
          here so you can revisit or reuse them later.
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <div className="loading-text">Loading…</div>
      ) : history.length === 0 ? (
        <div className="card empty-state">
          <h3>No AI history yet</h3>
          <p>Generate a negotiation strategy or settlement letter to see it appear here.</p>
        </div>
      ) : (
        history.map((h) => (
          <div className="card" key={h.history_id} style={{ marginBottom: 16 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                cursor: "pointer",
              }}
              onClick={() => toggle(h.history_id)}
            >
              <div>
                <div className="section-title" style={{ marginBottom: 4 }}>
                  Entry #{h.history_id}
                </div>
                <div className="strategy-meta" style={{ marginTop: 0 }}>
                  <span>SOURCE: {h.ai_response.toUpperCase()}</span>
                  <span>{new Date(h.generated_at).toLocaleString()}</span>
                </div>
              </div>
              <button className="secondary">{expandedId === h.history_id ? "Hide" : "View"}</button>
            </div>

            {expandedId === h.history_id && (
              <>
                <div style={{ marginTop: 16 }}>
                  <label>Negotiation Strategy</label>
                  <div className="strategy-box">{h.negotiation_strategy}</div>
                </div>
                <div style={{ marginTop: 16 }}>
                  <label>Settlement Letter</label>
                  <div className="strategy-box">{h.settlement_letter}</div>
                </div>
              </>
            )}
          </div>
        ))
      )}
    </div>
  );
}
