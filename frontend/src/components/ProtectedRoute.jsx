import { Navigate } from "react-router-dom";
import { useAuth } from "../api/AuthContext";

export default function ProtectedRoute({ children }) {
  const { token, loading } = useAuth();

  if (loading) return <div className="app-shell loading-text">Loading…</div>;
  if (!token) return <Navigate to="/login" replace />;

  return children;
}
