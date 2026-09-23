import { useState } from "react";
import api from "../api";

export default function SymptomAdvisor({ onPickDoctor }) {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const search = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const res = await api.get("/symptoms/lookup", { params: { q: query } });
      setResult(res.data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card advisor-card">
      <h3>Not sure who to see?</h3>
      <p className="muted">Describe a symptom and we'll suggest a specialist.</p>
      <form onSubmit={search} className="advisor-form">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. ear pain, headache, chest pain…"
        />
        <button className="btn primary" disabled={loading} type="submit">
          {loading ? "…" : "Check"}
        </button>
      </form>

      {result && (
        <div className="advisor-result">
          <p>{result.message}</p>
          {result.doctors?.length > 0 && (
            <ul className="advisor-doctor-list">
              {result.doctors.map((d) => (
                <li key={d.id}>
                  <span>
                    <strong>{d.name}</strong> — {d.specialty}
                  </span>
                  <button className="btn small" onClick={() => onPickDoctor(d)}>
                    Book with this doctor
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
