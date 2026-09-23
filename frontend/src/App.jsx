import { useEffect, useState } from "react";
import api from "./api";
import AuthForm from "./components/AuthForm";
import DoctorList from "./components/DoctorList";
import SymptomAdvisor from "./components/SymptomAdvisor";
import BookingPanel from "./components/BookingPanel";
import MyAppointments from "./components/MyAppointments";
import DiseaseTips from "./components/DiseaseTips";
import "./App.css";

export default function App() {
  const [user, setUser] = useState(null);
  const [checkingSession, setCheckingSession] = useState(true);
  const [bookingDoctor, setBookingDoctor] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [toast, setToast] = useState("");

  // Restore session on load if a token is already stored.
  useEffect(() => {
    const token = localStorage.getItem("mediconnect_token");
    if (!token) {
      setCheckingSession(false);
      return;
    }
    api
      .get("/auth/me")
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem("mediconnect_token"))
      .finally(() => setCheckingSession(false));
  }, []);

  const logout = () => {
    localStorage.removeItem("mediconnect_token");
    setUser(null);
  };

  const onBooked = () => {
    setBookingDoctor(null);
    setRefreshKey((k) => k + 1);
    setToast("Appointment booked!");
    setTimeout(() => setToast(""), 3000);
  };

  if (checkingSession) return null;

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">+</span>
          <div>
            <h1>MediConnect</h1>
            <span className="brand-tagline">Multispecialty Hospital &amp; Clinic Network</span>
          </div>
        </div>
        {user && (
          <div className="user-chip">
            <span>
              {user.name} <em>({user.role})</em>
            </span>
            <button className="btn small" onClick={logout}>
              Log out
            </button>
          </div>
        )}
      </header>

      {toast && <div className="toast">{toast}</div>}

      {!user ? (
        <main className="centered">
          <div className="hero">
            <h2>Quality care, made simple to book.</h2>
            <p>Find the right specialist, check real-time availability, and manage your appointments — all in one place.</p>
          </div>
          <AuthForm onAuth={(u) => setUser(u)} />
        </main>
      ) : (
        <main className="grid">
          <div className="col">
            {user.role === "patient" && (
              <SymptomAdvisor onPickDoctor={(d) => setBookingDoctor(d)} />
            )}
            <DoctorList onBook={(d) => setBookingDoctor(d)} />
            {user.role === "patient" && <DiseaseTips />}
          </div>
          <div className="col">
            <MyAppointments user={user} refreshKey={refreshKey} />
          </div>
        </main>
      )}

      {bookingDoctor && (
        <BookingPanel
          doctor={bookingDoctor}
          onClose={() => setBookingDoctor(null)}
          onBooked={onBooked}
        />
      )}

      <footer className="site-footer">
        <span>© {new Date().getFullYear()} MediConnect Hospital &amp; Clinic Network</span>
        <span className="muted small">
          For medical emergencies, call your local emergency number immediately.
        </span>
      </footer>
    </div>
  );
}
