import { useState } from "react";
import api from "../api";

export default function AuthForm({ onAuth }) {
  const [mode, setMode] = useState("login"); // "login" | "signup"
  const [role, setRole] = useState("patient");
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    specialty: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      let res;
      if (mode === "login") {
        res = await api.post("/auth/login", {
          email: form.email,
          password: form.password,
        });
      } else {
        res = await api.post("/auth/signup", {
          name: form.name,
          email: form.email,
          password: form.password,
          role,
          specialty: role === "doctor" ? form.specialty : undefined,
        });
      }
      const token = res.data.access_token;
      localStorage.setItem("mediconnect_token", token);
      const me = await api.get("/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });
      onAuth(me.data, token);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card auth-card">
      <h2>{mode === "login" ? "Log in" : "Create an account"}</h2>

      <div className="tab-row">
        <button
          className={mode === "login" ? "tab active" : "tab"}
          onClick={() => setMode("login")}
          type="button"
        >
          Log in
        </button>
        <button
          className={mode === "signup" ? "tab active" : "tab"}
          onClick={() => setMode("signup")}
          type="button"
        >
          Sign up
        </button>
      </div>

      <form onSubmit={submit}>
        {mode === "signup" && (
          <>
            <label>Name</label>
            <input value={form.name} onChange={update("name")} required />

            <label>I am a</label>
            <div className="role-toggle">
              <button
                type="button"
                className={role === "patient" ? "chip active" : "chip"}
                onClick={() => setRole("patient")}
              >
                Patient
              </button>
              <button
                type="button"
                className={role === "doctor" ? "chip active" : "chip"}
                onClick={() => setRole("doctor")}
              >
                Doctor
              </button>
            </div>

            {role === "doctor" && (
              <>
                <label>Specialty</label>
                <input
                  value={form.specialty}
                  onChange={update("specialty")}
                  placeholder="e.g. Cardiology"
                  required
                />
              </>
            )}
          </>
        )}

        <label>Email</label>
        <input type="email" value={form.email} onChange={update("email")} required />

        <label>Password</label>
        <input
          type="password"
          value={form.password}
          onChange={update("password")}
          minLength={6}
          required
        />

        {error && <p className="error">{error}</p>}

        <button className="btn primary" disabled={loading} type="submit">
          {loading ? "Please wait…" : mode === "login" ? "Log in" : "Sign up"}
        </button>
      </form>
    </div>
  );
}
