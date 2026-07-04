import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import FinancialHealth from "./pages/FinancialHealth";
import Loans from "./pages/Loans";
import Settlement from "./pages/Settlement";
import Negotiation from "./pages/Negotiation";
import KnowYourRights from "./pages/KnowYourRights";
import History from "./pages/History";
import { AuthProvider, useAuth } from "./api/AuthContext";

function AppShell({ children }) {
  const { token } = useAuth();
  return (
    <>
      {token && <Navbar />}
      {children}
    </>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/financial-health"
        element={
          <ProtectedRoute>
            <FinancialHealth />
          </ProtectedRoute>
        }
      />
      <Route
        path="/loans"
        element={
          <ProtectedRoute>
            <Loans />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settlement"
        element={
          <ProtectedRoute>
            <Settlement />
          </ProtectedRoute>
        }
      />
      <Route
        path="/negotiation"
        element={
          <ProtectedRoute>
            <Negotiation />
          </ProtectedRoute>
        }
      />
      <Route
        path="/rights"
        element={
          <ProtectedRoute>
            <KnowYourRights />
          </ProtectedRoute>
        }
      />
      <Route
        path="/history"
        element={
          <ProtectedRoute>
            <History />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppShell>
        <AppRoutes />
      </AppShell>
    </AuthProvider>
  );
}
