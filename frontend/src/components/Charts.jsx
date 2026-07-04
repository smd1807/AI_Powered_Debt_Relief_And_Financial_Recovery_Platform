import {
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

const scoreColor = (score) => {
  if (score >= 60) return "#33c48a";
  if (score >= 30) return "#e8ab3d";
  return "#e8555f";
};

export function HealthGauge({ score }) {
  const data = [{ name: "score", value: score, fill: scoreColor(score) }];
  return (
    <div style={{ width: "100%", height: 180, position: "relative" }}>
      <ResponsiveContainer>
        <RadialBarChart
          innerRadius="70%"
          outerRadius="100%"
          data={data}
          startAngle={180}
          endAngle={0}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
          <RadialBar dataKey="value" cornerRadius={8} background={{ fill: "#232b45" }} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div
        style={{
          position: "absolute",
          top: "58%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          textAlign: "center",
        }}
      >
        <div style={{ fontFamily: "IBM Plex Mono, monospace", fontSize: 34, fontWeight: 600, color: "#e8ecf7" }}>
          {score}
        </div>
        <div style={{ fontSize: 11, color: "#8b93ac", fontFamily: "IBM Plex Mono, monospace" }}>
          HEALTH SCORE
        </div>
      </div>
    </div>
  );
}

export function DebtBreakdownChart({ loans }) {
  const data = loans.map((l) => ({
    name: l.lender_name.length > 12 ? l.lender_name.slice(0, 12) + "…" : l.lender_name,
    outstanding: l.outstanding_amount,
  }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#232b45" vertical={false} />
        <XAxis dataKey="name" tick={{ fontSize: 11, fontFamily: "Inter", fill: "#8b93ac" }} />
        <YAxis tick={{ fontSize: 11, fontFamily: "IBM Plex Mono", fill: "#8b93ac" }} />
        <Tooltip
          formatter={(v) => `₹${Number(v).toLocaleString("en-IN")}`}
          contentStyle={{
            fontFamily: "Inter",
            fontSize: 13,
            borderRadius: 8,
            background: "#161d33",
            border: "1px solid #232b45",
            color: "#e8ecf7",
          }}
        />
        <Bar dataKey="outstanding" fill="#4f7dff" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function DebtTimelineChart({ timeline }) {
  const data = timeline.map((t) => ({
    month: `M${t.month}`,
    balance: t.remaining_balance,
  }));

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#232b45" vertical={false} />
        <XAxis dataKey="month" tick={{ fontSize: 11, fontFamily: "Inter", fill: "#8b93ac" }} />
        <YAxis tick={{ fontSize: 11, fontFamily: "IBM Plex Mono", fill: "#8b93ac" }} />
        <Tooltip
          formatter={(v) => `₹${Number(v).toLocaleString("en-IN")}`}
          contentStyle={{
            fontFamily: "Inter",
            fontSize: 13,
            borderRadius: 8,
            background: "#161d33",
            border: "1px solid #232b45",
            color: "#e8ecf7",
          }}
        />
        <Bar dataKey="balance" fill="#33c48a" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
