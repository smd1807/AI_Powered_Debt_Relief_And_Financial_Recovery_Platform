const RIGHTS = [
  {
    icon: "🛡️",
    title: "No Harassment",
    text: "Recovery agents cannot threaten, abuse, or harass you — verbally or physically — at any time or place, including your workplace.",
  },
  {
    icon: "🕐",
    title: "Right to Fair Timing",
    text: "Collection calls and visits are only permitted between 8 AM and 7 PM. Contact outside this window is a violation of RBI guidelines.",
  },
  {
    icon: "📝",
    title: "Settlement in Writing",
    text: "Never make a payment based on a verbal promise. Always insist on a written settlement agreement before transferring any money.",
  },
  {
    icon: "🔒",
    title: "Privacy Protection",
    text: "Lenders cannot disclose your debt details to your employer, neighbors, or family members without your explicit consent.",
  },
  {
    icon: "⚖️",
    title: "Right to Dispute",
    text: "If you believe an amount is incorrect, you can formally dispute it in writing and request full account statements before paying.",
  },
  {
    icon: "📄",
    title: "No-Dues Certificate",
    text: "After a settlement is paid in full, you're entitled to a written no-dues certificate and an updated credit bureau report.",
  },
  {
    icon: "🤝",
    title: "Right to Negotiate",
    text: "You are always allowed to propose a realistic, affordable settlement rather than being forced into a payment plan you can't sustain.",
  },
  {
    icon: "🚫",
    title: "No Illegal Recovery",
    text: "Agents cannot seize property, threaten legal action they have no authority to take, or visit in groups intended to intimidate.",
  },
];

const NEXT_STEPS = [
  { title: "Document everything", text: "Keep records of every call, message, and visit from collection agents." },
  { title: "Request in writing", text: "Ask for all settlement offers and account details in writing before agreeing." },
  { title: "File a complaint", text: "Report harassment or illegal practices to your lender's grievance cell or the RBI Ombudsman." },
  { title: "Seek help early", text: "Reach out to a financial counselor or legal aid service if a situation feels overwhelming." },
];

export default function KnowYourRights() {
  return (
    <div className="app-shell">
      <div className="page-header">
        <span className="page-eyebrow">Know Your Rights</span>
        <h1>You Have Rights as a Borrower 💪</h1>
        <p>
          Understand your legal protections against unfair debt collection practices, so you can
          negotiate from a position of confidence and strength.
        </p>
      </div>

      <div className="rights-grid" style={{ marginBottom: 32 }}>
        {RIGHTS.map((r) => (
          <div className="rights-card" key={r.title}>
            <div className="rights-icon">{r.icon}</div>
            <h3>{r.title}</h3>
            <p>{r.text}</p>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="section-title">What To Do If Harassed</div>
        <div className="rights-grid">
          {NEXT_STEPS.map((s) => (
            <div key={s.title}>
              <h3 style={{ fontSize: 14, marginBottom: 4 }}>{s.title}</h3>
              <p style={{ fontSize: 13, color: "var(--text-soft)", margin: 0 }}>{s.text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
