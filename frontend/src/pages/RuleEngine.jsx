import { useState } from "react";
import { rules as initial } from "../data/mockData.js";

export default function RuleEngine() {
  const [rules, setRules] = useState(initial);
  const toggle = (id) => setRules((rs) => rs.map((r) => (r.id === id ? { ...r, active: !r.active } : r)));

  return (
    <div className="page-simple">
      <h1 className="page-title">Rules Engine</h1>
      <p className="muted">Manage regulatory validation rules.</p>

      <div className="card">
        <div className="table-wrap">
          <table className="table">
            <thead><tr><th>Rule ID</th><th>Regulator</th><th>Name</th><th>Severity</th><th>Active</th></tr></thead>
            <tbody>
              {rules.map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td><td>{r.regulator}</td><td>{r.name}</td>
                  <td><span className={`impact ${r.severity.toLowerCase()}`}>{r.severity}</span></td>
                  <td>
                    <label className="switch">
                      <input type="checkbox" checked={r.active} onChange={() => toggle(r.id)} />
                      <span />
                    </label>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
