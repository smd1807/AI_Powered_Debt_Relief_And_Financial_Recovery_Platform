/**
 * Central API client (Epic 4: "Frontend communicates with FastAPI")
 * Attaches the JWT bearer token to every request automatically, and
 * matches the exact backend endpoint set: /register, /login, /add-loan,
 * /loans, /delete-loan/{id}, /update-profile, /dashboard-data,
 * /financial-health, /debt-timeline, /settlement-predictor,
 * /ai-negotiation-strategy, /generate-negotiation-email/{loan_id}, /ai-history.
 */
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("finrelief_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: handle unauthorized responses automatically.
// If the backend returns 401 (expired/invalid token), clear the stored
// token and redirect the user to the login page.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const isAuthRoute =
      error?.config?.url === "/login" || error?.config?.url === "/register";
    if (status === 401 && !isAuthRoute) {
      localStorage.removeItem("finrelief_token");
      if (window.location.pathname !== "/login") {
        window.location.assign("/login");
      }
    }
    return Promise.reject(error);
  }
);

// ---------- Auth ----------
export const registerUser = (payload) => api.post("/register", payload).then((r) => r.data);
export const loginUser = (payload) => api.post("/login", payload).then((r) => r.data);
export const getCurrentUser = () => api.get("/debug-user").then((r) => r.data);

// ---------- Loans ----------
export const createLoan = (payload) => api.post("/add-loan", payload).then((r) => r.data);
export const listLoans = () => api.get("/loans").then((r) => r.data);
export const deleteLoan = (id) => api.delete(`/delete-loan/${id}`).then((r) => r.data);

// ---------- Financial Profile ----------
export const updateProfile = (payload) => api.put("/update-profile", payload).then((r) => r.data);
export const getDashboardData = () => api.get("/dashboard-data").then((r) => r.data);
export const getFinancialHealth = () => api.get("/financial-health").then((r) => r.data);
export const getDebtTimeline = (extraPayment = 0) =>
  api.get("/debt-timeline", { params: { extra_payment: extraPayment } }).then((r) => r.data);

// ---------- Settlement ----------
export const predictSettlement = (loanId) =>
  api
    .get("/settlement-predictor", { params: loanId ? { loan_id: loanId } : {} })
    .then((r) => r.data);

// ---------- AI History ----------
export const generateNegotiationStrategy = (loanId) =>
  api
    .get("/ai-negotiation-strategy", { params: loanId ? { loan_id: loanId } : {} })
    .then((r) => r.data);
export const generateNegotiationEmail = (loanId) =>
  api.get(`/generate-negotiation-email/${loanId}`).then((r) => r.data);
export const getAIHistory = () => api.get("/ai-history").then((r) => r.data);

export default api;
