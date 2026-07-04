import { createContext, useContext, useState, useEffect } from "react";
import { getCurrentUser } from "./client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("finrelief_token"));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    getCurrentUser()
      .then(setUser)
      .catch(() => {
        // Token invalid/expired -> clear it
        localStorage.removeItem("finrelief_token");
        setToken(null);
      })
      .finally(() => setLoading(false));
  }, [token]);

  const login = (newToken) => {
    localStorage.setItem("finrelief_token", newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem("finrelief_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
