import { useEffect, useState } from "react";
import { listLoans, createLoan, deleteLoan } from "../api/client";

const LOAN_TYPES = [
  { value: "credit_card", label: "Credit Card" },
  { value: "personal_loan", label: "Personal Loan" },
  { value: "home_loan", label: "Home Loan" },
  { value: "vehicle_loan", label: "Vehicle Loan" },
  { value: "business_loan", label: "Business Loan" },
  { value: "other", label: "Other" },
];

const emptyForm = {
  lender_name: "",
  loan_type: "credit_card",
  loan_amount: "",
  outstanding_amount: "",
  interest_rate: "",
  emi: "",
  months_overdue: "0",
  due_date: "",
};

export default function Loans() {
  const [loans, setLoans] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    listLoans()
      .then(setLoans)
      .catch(() => setError("Could not load loans."))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await createLoan({
        lender_name: form.lender_name,
        loan_type: form.loan_type,
        loan_amount: Number(form.loan_amount),
        outstanding_amount: Number(form.outstanding_amount),
        interest_rate: Number(form.interest_rate) || 0,
        emi: Number(form.emi) || 0,
        months_overdue: Number(form.months_overdue) || 0,
        due_date: form.due_date || null,
      });
      setForm(emptyForm);
      load();
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not add this loan. Check the values and try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    await deleteLoan(id);
    load();
  };

  const inr = (n) => `₹${Number(n).toLocaleString("en-IN")}`;

  return (
    <div className="app-shell">
      <div className="page-header">
        <span className="page-eyebrow">Loans</span>
        <h1>Manage Your Loans</h1>
        <p>Add every loan/debt you're carrying so the AI has the full picture to work with.</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <form className="card" onSubmit={handleSubmit} style={{ marginBottom: 24 }}>
        <div className="section-title">Add a loan</div>
        <div className="form-grid">
          <div>
            <label>Lender name</label>
            <input
              name="lender_name"
              value={form.lender_name}
              onChange={handleChange}
              placeholder="e.g. HDFC Bank"
              required
            />
          </div>
          <div>
            <label>Loan type</label>
            <select name="loan_type" value={form.loan_type} onChange={handleChange}>
              {LOAN_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label>Original loan amount (₹)</label>
            <input
              type="number"
              name="loan_amount"
              value={form.loan_amount}
              onChange={handleChange}
              min="0"
              required
            />
          </div>
          <div>
            <label>Outstanding amount (₹)</label>
            <input
              type="number"
              name="outstanding_amount"
              value={form.outstanding_amount}
              onChange={handleChange}
              min="0"
              required
            />
          </div>
          <div>
            <label>Monthly EMI (₹)</label>
            <input
              type="number"
              name="emi"
              value={form.emi}
              onChange={handleChange}
              min="0"
              required
            />
          </div>
          <div>
            <label>Interest rate (% p.a.)</label>
            <input
              type="number"
              name="interest_rate"
              value={form.interest_rate}
              onChange={handleChange}
              min="0"
              step="0.1"
            />
          </div>
          <div>
            <label>Months overdue</label>
            <input
              type="number"
              name="months_overdue"
              value={form.months_overdue}
              onChange={handleChange}
              min="0"
            />
          </div>
          <div>
            <label>Due date (optional)</label>
            <input type="date" name="due_date" value={form.due_date} onChange={handleChange} />
          </div>
        </div>
        <button type="submit" disabled={submitting}>
          {submitting ? "Adding..." : "Add loan"}
        </button>
      </form>

      <div className="card">
        <div className="section-title">Your loans</div>
        {loading ? (
          <div className="loading-text">Loading…</div>
        ) : loans.length === 0 ? (
          <div className="empty-state">
            <h3>No loans added yet</h3>
            <p>Use the form above to add your first one.</p>
          </div>
        ) : (
          loans.map((l) => (
            <div className="debt-row" key={l.loan_id}>
              <div>
                <div className="creditor">{l.lender_name}</div>
                <div className="debt-type">{l.loan_type.replace("_", " ")}</div>
              </div>
              <div className="mono">{inr(l.outstanding_amount)}</div>
              <div className="mono">EMI {inr(l.emi)}</div>
              <div className="mono">{l.months_overdue}mo overdue</div>
              <button className="secondary" onClick={() => handleDelete(l.loan_id)}>
                Remove
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
