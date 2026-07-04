import { useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../api/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  const linkClass = ({ isActive }) => (isActive ? "active" : "");
  const closeMenu = () => setMenuOpen(false);

  return (
    <div className="navbar">
      <div className="brand">
        <span className="brand-icon">💠</span>
        <span className="brand-mark">FinRelief AI</span>
      </div>

      <button
        className="nav-toggle"
        aria-label="Toggle menu"
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen((open) => !open)}
      >
        <span />
        <span />
        <span />
      </button>

      <nav className={menuOpen ? "open" : ""}>
        <NavLink to="/" end className={linkClass} onClick={closeMenu}>
          Dashboard
        </NavLink>
        <NavLink to="/financial-health" className={linkClass} onClick={closeMenu}>
          Financial Health
        </NavLink>
        <NavLink to="/loans" className={linkClass} onClick={closeMenu}>
          Loans
        </NavLink>
        <NavLink to="/settlement" className={linkClass} onClick={closeMenu}>
          Settlement Predictor
        </NavLink>
        <NavLink to="/negotiation" className={linkClass} onClick={closeMenu}>
          Negotiation
        </NavLink>
        <NavLink to="/rights" className={linkClass} onClick={closeMenu}>
          Know Your Rights
        </NavLink>
        <NavLink to="/history" className={linkClass} onClick={closeMenu}>
          History
        </NavLink>
        <button
          className="logout-btn logout-btn-mobile"
          onClick={() => {
            closeMenu();
            logout();
          }}
        >
          Sign Out
        </button>
      </nav>

      <button className="logout-btn logout-btn-desktop" onClick={logout} title={user?.email}>
        Sign Out
      </button>
    </div>
  );
}
