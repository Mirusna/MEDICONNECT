import { useEffect, useState } from "react";
import api from "../api";

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function fmtTime(iso) {
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function BookingPanel({ doctor, onClose, onBooked }) {
  const [date, setDate] = useState(todayISO());
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [booking, setBooking] = useState(false);
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError("");
    setSelected(null);
    api
      .get(`/doctors/${doctor.id}/slots`, { params: { for_date: date } })
      .then((res) => {
        if (!cancelled) setSlots(res.data);
      })
      .catch(() => !cancelled && setError("Could not load slots"))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [doctor.id, date]);

  const book = async () => {
    if (!selected) return;
    setBooking(true);
    setError("");
    try {
      await api.post("/appointments", {
        doctor_id: doctor.id,
        start_time: selected.start_time,
        end_time: selected.end_time,
        reason,
      });
      onBooked();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not book that slot");
      // Slot may have just been taken — refresh the list.
      const res = await api.get(`/doctors/${doctor.id}/slots`, { params: { for_date: date } });
      setSlots(res.data);
      setSelected(null);
    } finally {
      setBooking(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ×
        </button>
        <h3>Book with {doctor.name}</h3>
        <p className="muted">{doctor.specialty}</p>

        <label>Date</label>
        <input
          type="date"
          value={date}
          min={todayISO()}
          onChange={(e) => setDate(e.target.value)}
        />

        <label>Available slots</label>
        {loading ? (
          <p className="muted">Loading slots…</p>
        ) : slots.length === 0 ? (
          <p className="muted">No open slots this day. Try another date.</p>
        ) : (
          <div className="slot-grid">
            {slots.map((s) => (
              <button
                key={s.start_time}
                className={
                  selected?.start_time === s.start_time ? "slot active" : "slot"
                }
                onClick={() => setSelected(s)}
                type="button"
              >
                {fmtTime(s.start_time)}
              </button>
            ))}
          </div>
        )}

        <label>Reason for visit (optional)</label>
        <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="e.g. follow-up, ear pain" />

        {error && <p className="error">{error}</p>}

        <button className="btn primary" disabled={!selected || booking} onClick={book}>
          {booking ? "Booking…" : selected ? `Confirm ${fmtTime(selected.start_time)}` : "Pick a slot"}
        </button>
      </div>
    </div>
  );
}
