import { useEffect, useState } from "react";
import api from "../api";

function fmt(iso) {
  const d = new Date(iso);
  return d.toLocaleString([], {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function MyAppointments({ user, refreshKey }) {
  const [appts, setAppts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cancellingId, setCancellingId] = useState(null);

  const load = () => {
    setLoading(true);
    api
      .get("/appointments/me")
      .then((res) => setAppts(res.data))
      .finally(() => setLoading(false));
  };

  useEffect(load, [refreshKey]);

  const cancel = async (id) => {
    setCancellingId(id);
    try {
      await api.post(`/appointments/${id}/cancel`);
      load();
    } finally {
      setCancellingId(null);
    }
  };

  return (
    <div className="card">
      <h3>{user.role === "doctor" ? "Your schedule" : "My appointments"}</h3>
      {loading ? (
        <p className="muted">Loading…</p>
      ) : appts.length === 0 ? (
        <p className="muted">No appointments yet.</p>
      ) : (
        <ul className="appt-list">
          {appts
            .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
            .map((a) => (
              <li key={a.id} className={`appt-row status-${a.status}`}>
                <div>
                  <strong>{fmt(a.start_time)}</strong>
                  <p className="muted">
                    {user.role === "doctor" ? a.patient_name : `${a.doctor_name} — ${a.doctor_specialty}`}
                  </p>
                  {a.reason && <p className="muted small">Reason: {a.reason}</p>}
                  <span className={`status-badge ${a.status}`}>{a.status}</span>
                </div>
                {a.status === "booked" && (
                  <button
                    className="btn small danger"
                    disabled={cancellingId === a.id}
                    onClick={() => cancel(a.id)}
                  >
                    {cancellingId === a.id ? "Cancelling…" : "Cancel"}
                  </button>
                )}
              </li>
            ))}
        </ul>
      )}
    </div>
  );
}
