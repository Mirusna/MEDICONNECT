import { useEffect, useState } from "react";
import api from "../api";

export default function DoctorList({ onBook, jumpDoctorId }) {
  const [doctors, setDoctors] = useState([]);
  const [specialty, setSpecialty] = useState("");
  const [loading, setLoading] = useState(true);

  const load = (spec) => {
    setLoading(true);
    api
      .get("/doctors", { params: spec ? { specialty: spec } : {} })
      .then((res) => setDoctors(res.data))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const onFilter = (e) => {
    e.preventDefault();
    load(specialty);
  };

  return (
    <div className="card">
      <h3>Find a doctor</h3>
      <form onSubmit={onFilter} className="filter-row">
        <input
          value={specialty}
          onChange={(e) => setSpecialty(e.target.value)}
          placeholder="Filter by specialty (e.g. Cardiology)"
        />
        <button className="btn" type="submit">
          Filter
        </button>
        {specialty && (
          <button
            className="btn"
            type="button"
            onClick={() => {
              setSpecialty("");
              load();
            }}
          >
            Clear
          </button>
        )}
      </form>

      {loading ? (
        <p className="muted">Loading doctors…</p>
      ) : doctors.length === 0 ? (
        <p className="muted">No doctors match that specialty.</p>
      ) : (
        <ul className="doctor-list">
          {doctors.map((d) => (
            <li key={d.id} className={jumpDoctorId === d.id ? "doctor-row highlight" : "doctor-row"}>
              <div>
                <strong>{d.name}</strong>
                <span className="badge">{d.specialty}</span>
                <p className="muted">{d.bio}</p>
                <p className="muted small">{d.years_experience} yrs experience</p>
              </div>
              <button className="btn primary" onClick={() => onBook(d)}>
                Book
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
