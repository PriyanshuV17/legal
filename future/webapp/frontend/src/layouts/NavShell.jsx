import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import BrandMark from "../components/BrandMark";
import { api } from "../api";

const publicLinks = [
  ["/", "Home"],
  ["/about", "About"],
  ["/contact", "Contact"]
];

const userLinks = [
  ["/dashboard", "Dashboard"],
  ["/chat", "Chat Assistant"],
  ["/cases", "Case Explorer"],
  ["/laws", "Law Explorer"],
  ["/lawyers", "Lawyer Match"],
  ["/booking", "Book Lawyer"],
  ["/bookings", "My Bookings"],
  ["/appointments", "My Appointments"],
  ["/my-cases", "My Cases"],
  ["/profile", "Profile"]
];

const adminLinks = [
  ["/admin", "Admin Dashboard"],
  ["/admin/users", "Users"],
  ["/admin/lawyers", "Lawyers"],
  ["/admin/content", "Content"],
  ["/admin/bookings", "Bookings"],
  ["/admin/analytics", "Analytics"]
];

export default function NavShell({ user, setUser }) {
  const navigate = useNavigate();
  const location = useLocation();
  const links = [...publicLinks];
  if (user) {
    links.push(...userLinks);
    if (user.role === "lawyer") links.push(["/lawyer", "Lawyer Hub"]);
    if (user.role === "admin") links.push(...adminLinks);
  }

  useEffect(() => {
    api.post("/activity", {
      actor_user_id: user?.id ?? null,
      event_type: "page_view",
      detail: `Visited ${location.pathname}`
    }).catch(() => {});
  }, [location.pathname, user]);

  return (
    <div className="app-shell">
      <div className="watermark-layer">
        <BrandMark watermark />
      </div>
      <header className="topbar">
        <Link className="brand-link" to="/">
          <BrandMark />
        </Link>
        <nav className="topnav">
          {links.map(([to, label]) => (
            <NavLink key={to} to={to} className={({ isActive }) => (isActive ? "active" : "")}>
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="topbar-actions">
          {user ? (
            <>
              <div className="profile-pill">
                <span>{user.name}</span>
                <small>{user.role}</small>
              </div>
              <button
                className="ghost-button"
                onClick={() => {
                  localStorage.removeItem("legalbuddy_user");
                  setUser(null);
                  navigate("/");
                }}
              >
                Logout
              </button>
            </>
          ) : (
            <Link className="primary-button" to="/auth">
              Login / Register
            </Link>
          )}
        </div>
      </header>
      <main className="page-wrap">
        <Outlet />
      </main>
    </div>
  );
}
