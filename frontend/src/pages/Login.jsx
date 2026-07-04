import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { registerUser, loginUser } from "../api/client";
import { useAuth } from "../api/AuthContext";

export default function Login() {
  const { login, token } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState("signin"); // signin | register
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Already authenticated (e.g. token in localStorage) -> go to dashboard
  if (token) return <Navigate to="/" replace />;

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      if (mode === "register") {
        await registerUser({ name: form.name, email: form.email, password: form.password });
      }
      const result = await loginUser({ email: form.email, password: form.password });
      login(result.access_token);
      navigate("/", { replace: true });
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          (mode === "register" ? "Could not create your account." : "Incorrect email or password.")
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="auth-hero">
          <div className="brand-icon">💠</div>
          <h1>
            Take Control of Your <span className="accent-word">Financial Future</span>
          </h1>
          <p>Sign in to your dashboard</p>
        </div>

        <div className="auth-tabs">
          <button
            className={mode === "signin" ? "active" : ""}
            onClick={() => setMode("signin")}
            type="button"
          >
            Sign In
          </button>
          <button
            className={mode === "register" ? "active" : ""}
            onClick={() => setMode("register")}
            type="button"
          >
            Register
          </button>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <form className="card" onSubmit={handleSubmit}>
          {mode === "register" && (
            <div style={{ marginBottom: 14 }}>
              <label>Full name</label>
              <input name="name" value={form.name} onChange={handleChange} required />
            </div>
          )}
          <div style={{ marginBottom: 14 }}>
            <label>Email address</label>
            <input
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="you@example.com"
              required
            />
          </div>
          <div style={{ marginBottom: 18 }}>
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
              minLength={6}
            />
          </div>
          <button type="submit" disabled={submitting} style={{ width: "100%" }}>
            {submitting
              ? "Please wait..."
              : mode === "signin"
              ? "Sign In →"
              : "Create account →"}
          </button>
        </form>

        <div className="auth-tags">
          <span className="auth-tag">40-75% Settlement Range</span>
          <span className="auth-tag">AI Financial Strategy</span>
          <span className="auth-tag">Free to Get Started</span>
        </div>
      </div>
    </div>
  );
}
