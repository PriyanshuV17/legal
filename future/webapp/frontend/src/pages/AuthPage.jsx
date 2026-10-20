import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const initialRegister = {
  name: "",
  city: "",
  state: "",
  phone: "",
  email: "",
  age: 18,
  profession: "Need Legal Help",
  language: "English",
  password: ""
};

export default function AuthPage({ setUser }) {
  const [mode, setMode] = useState("login");
  const [loginData, setLoginData] = useState({ identifier: "", password: "" });
  const [registerData, setRegisterData] = useState(initialRegister);
  const [resetData, setResetData] = useState({ identifier: "", new_password: "" });
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  async function handleLogin(event) {
    event.preventDefault();
    const { data } = await api.post("/auth/login", loginData);
    localStorage.setItem("legalbuddy_user", JSON.stringify(data.user));
    setUser(data.user);
    navigate(data.user.role === "admin" ? "/admin" : "/dashboard");
  }

  async function handleRegister(event) {
    event.preventDefault();
    await api.post("/auth/register", registerData);
    setMessage("Account created. You can log in now.");
    setMode("login");
  }

  async function handleReset(event) {
    event.preventDefault();
    await api.post("/auth/reset-password", resetData);
    setMessage("Password updated. Please log in.");
    setMode("login");
  }

  return (
    <div className="page auth-grid">
      <div className="glass-card auth-panel">
        <div className="tab-row">
          <button className={mode === "login" ? "tab active" : "tab"} onClick={() => setMode("login")}>Login</button>
          <button className={mode === "register" ? "tab active" : "tab"} onClick={() => setMode("register")}>Register</button>
          <button className={mode === "reset" ? "tab active" : "tab"} onClick={() => setMode("reset")}>Reset</button>
        </div>
        {mode === "login" ? (
          <form className="stack" onSubmit={handleLogin}>
            <h2>Welcome back</h2>
            <input placeholder="Email or mobile" value={loginData.identifier} onChange={(e) => setLoginData({ ...loginData, identifier: e.target.value })} />
            <input type="password" placeholder="Password" value={loginData.password} onChange={(e) => setLoginData({ ...loginData, password: e.target.value })} />
            <button className="primary-button" type="submit">Login</button>
            <p className="muted-text">Use Reset if you need to change your password.</p>
          </form>
        ) : mode === "register" ? (
          <form className="stack" onSubmit={handleRegister}>
            <h2>Create your account</h2>
            <input placeholder="Full name" value={registerData.name} onChange={(e) => setRegisterData({ ...registerData, name: e.target.value })} />
            <div className="form-row">
              <input placeholder="City" value={registerData.city} onChange={(e) => setRegisterData({ ...registerData, city: e.target.value })} />
              <input placeholder="State" value={registerData.state} onChange={(e) => setRegisterData({ ...registerData, state: e.target.value })} />
            </div>
            <div className="form-row">
              <input placeholder="Mobile" value={registerData.phone} onChange={(e) => setRegisterData({ ...registerData, phone: e.target.value })} />
              <input placeholder="Email" value={registerData.email} onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })} />
            </div>
            <div className="form-row">
              <input type="number" placeholder="Age" value={registerData.age} onChange={(e) => setRegisterData({ ...registerData, age: Number(e.target.value) })} />
              <select value={registerData.profession} onChange={(e) => setRegisterData({ ...registerData, profession: e.target.value })}>
                <option>Student / Learner</option>
                <option>Need Legal Help</option>
                <option>Lawyer</option>
              </select>
            </div>
            <div className="form-row">
              <select value={registerData.language} onChange={(e) => setRegisterData({ ...registerData, language: e.target.value })}>
                <option>English</option>
                <option>Hindi</option>
              </select>
              <input type="password" placeholder="Create password" value={registerData.password} onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })} />
            </div>
            <button className="primary-button" type="submit">Create account</button>
          </form>
        ) : (
          <form className="stack" onSubmit={handleReset}>
            <h2>Reset password</h2>
            <input placeholder="Registered email or mobile" value={resetData.identifier} onChange={(e) => setResetData({ ...resetData, identifier: e.target.value })} />
            <input type="password" placeholder="New password" value={resetData.new_password} onChange={(e) => setResetData({ ...resetData, new_password: e.target.value })} />
            <button className="primary-button" type="submit">Update password</button>
          </form>
        )}
        {message && <p className="success-text">{message}</p>}
      </div>
      <div className="glass-card hero-mini">
        <h3>Everything stored for retrieval</h3>
        <p>User profiles, chat sessions, messages, contact submissions, bookings, saved laws, saved cases, and audit logs live in the backend database. Semantic memory is also stored for smart recall.</p>
      </div>
    </div>
  );
}
