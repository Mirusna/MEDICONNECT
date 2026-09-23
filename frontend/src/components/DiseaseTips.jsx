import { useEffect, useState } from "react";
import api from "../api";

const AGE_GROUPS = [
  { key: "children", label: "Children" },
  { key: "teen", label: "Teens" },
  { key: "adult", label: "Adults" },
  { key: "senior", label: "Senior Citizens" },
];

export default function DiseaseTips() {
  const [names, setNames] = useState([]);
  const [selected, setSelected] = useState("");
  const [ageGroup, setAgeGroup] = useState("adult");
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/diseases").then((res) => setNames(res.data));
  }, []);

  useEffect(() => {
    if (!selected) {
      setData(null);
      return;
    }
    api.get(`/diseases/${encodeURIComponent(selected)}/tips`).then((res) => setData(res.data));
  }, [selected]);

  if (names.length === 0) return null;

  const activeTip =
    data?.age_specific?.find((t) => t.age_group === ageGroup) ||
    (data
      ? { diet_dos: data.diet_dos, diet_donts: data.diet_donts, general_tips: data.general_tips }
      : null);

  return (
    <div className="card">
      <h3>Diet & Care Chart</h3>
      <p className="muted">Guidance tailored by condition and age group.</p>

      <label>Condition</label>
      <select value={selected} onChange={(e) => setSelected(e.target.value)}>
        <option value="">Choose a condition…</option>
        {names.map((n) => (
          <option key={n} value={n}>
            {n[0].toUpperCase() + n.slice(1)}
          </option>
        ))}
      </select>

      {data && (
        <>
          <label>Age group</label>
          <div className="age-tabs">
            {AGE_GROUPS.map((g) => (
              <button
                key={g.key}
                type="button"
                className={ageGroup === g.key ? "chip active" : "chip"}
                onClick={() => setAgeGroup(g.key)}
              >
                {g.label}
              </button>
            ))}
          </div>

          {activeTip && (
            <div className="tips-block">
              <p>
                <strong>Do:</strong> {activeTip.diet_dos}
              </p>
              <p>
                <strong>Avoid:</strong> {activeTip.diet_donts}
              </p>
              <p>
                <strong>General tips:</strong> {activeTip.general_tips}
              </p>
              <p className="muted small">
                This is general guidance, not medical advice — always confirm with your doctor.
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
