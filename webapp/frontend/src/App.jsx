import { Navigate, Route, Routes } from "react-router-dom";
import { useMemo, useState } from "react";
import NavShell from "./layouts/NavShell";
import HomePage from "./pages/HomePage";
import AboutPage from "./pages/AboutPage";
import ContactPage from "./pages/ContactPage";
import AuthPage from "./pages/AuthPage";
import UserDashboardPage from "./pages/UserDashboardPage";
import ChatPage from "./pages/ChatPage";
import CaseExplorerPage from "./pages/CaseExplorerPage";
import LawExplorerPage from "./pages/LawExplorerPage";
import LawyersPage from "./pages/LawyersPage";
import BookingPage from "./pages/BookingPage";
import MyCasesPage from "./pages/MyCasesPage";
import ProfilePage from "./pages/ProfilePage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import LawyerHubPage from "./pages/LawyerHubPage";
import AdminUserDetailPage from "./pages/AdminUserDetailPage";
import AdminUsersPage from "./pages/AdminUsersPage";
import AdminLawyersPage from "./pages/AdminLawyersPage";
import AdminBookingsPage from "./pages/AdminBookingsPage";
import AdminAnalyticsPage from "./pages/AdminAnalyticsPage";
import AdminContentPage from "./pages/AdminContentPage";

function ProtectedRoute({ user, children }) {
  if (!user) return <Navigate to="/auth" replace />;
  return children;
}

function RoleRoute({ user, role, children }) {
  if (!user) return <Navigate to="/auth" replace />;
  if (user.role !== role) return <Navigate to="/dashboard" replace />;
  return children;
}

export default function App() {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("legalbuddy_user");
    return stored ? JSON.parse(stored) : null;
  });

  const shellProps = useMemo(() => ({ user, setUser }), [user]);

  return (
    <Routes>
      <Route element={<NavShell {...shellProps} />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/auth" element={<AuthPage setUser={setUser} />} />
        <Route path="/dashboard" element={<ProtectedRoute user={user}><UserDashboardPage user={user} /></ProtectedRoute>} />
        <Route path="/chat" element={<ProtectedRoute user={user}><ChatPage user={user} /></ProtectedRoute>} />
        <Route path="/cases" element={<ProtectedRoute user={user}><CaseExplorerPage user={user} /></ProtectedRoute>} />
        <Route path="/laws" element={<ProtectedRoute user={user}><LawExplorerPage user={user} /></ProtectedRoute>} />
        <Route path="/lawyers" element={<ProtectedRoute user={user}><LawyersPage /></ProtectedRoute>} />
        <Route path="/booking" element={<ProtectedRoute user={user}><BookingPage user={user} /></ProtectedRoute>} />
        <Route path="/my-cases" element={<ProtectedRoute user={user}><MyCasesPage user={user} /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute user={user}><ProfilePage user={user} setUser={setUser} /></ProtectedRoute>} />
        <Route path="/lawyer" element={<RoleRoute user={user} role="lawyer"><LawyerHubPage /></RoleRoute>} />
        <Route path="/admin" element={<RoleRoute user={user} role="admin"><AdminDashboardPage /></RoleRoute>} />
        <Route path="/admin/users" element={<RoleRoute user={user} role="admin"><AdminUsersPage /></RoleRoute>} />
        <Route path="/admin/users/:userId" element={<RoleRoute user={user} role="admin"><AdminUserDetailPage /></RoleRoute>} />
        <Route path="/admin/lawyers" element={<RoleRoute user={user} role="admin"><AdminLawyersPage /></RoleRoute>} />
        <Route path="/admin/content" element={<RoleRoute user={user} role="admin"><AdminContentPage /></RoleRoute>} />
        <Route path="/admin/bookings" element={<RoleRoute user={user} role="admin"><AdminBookingsPage /></RoleRoute>} />
        <Route path="/admin/analytics" element={<RoleRoute user={user} role="admin"><AdminAnalyticsPage /></RoleRoute>} />
      </Route>
    </Routes>
  );
}
