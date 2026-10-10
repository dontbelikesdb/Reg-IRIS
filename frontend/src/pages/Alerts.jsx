import { useState } from "react";
import { alerts as initial } from "../data/mockData.js";

export default function Alerts() {
  const [alerts, setAlerts] = useState(initial);
  const [level, setLevel] = useState("All");
  const unread = alerts.filter((a) => !a.read).length;
  const shown = alerts.filter((a) => level === "All" || a.level === level);
  const markRead = (id) => setAlerts((as) => as.map((a) => (a.id === id ? { ...a, read: true } : a)));

  return (
    <div className="page-simple">
      <h1 className="page-title">Alerts</h1>
      <p className="muted">{unread} unread alert{unread !== 1 && "s"}.</p>

      <div className="toolbar-row">
        <div className="chip-row">
          {["All", "High", "Medium", "Low"].map((l) => (
            <button key={l} className={`chip${level === l ? " active" : ""}`} onClick={() => setLevel(l)}>{l}</button>
          ))}
        </div>
        <button className="btn ghost" onClick={() => setAlerts((as) => as.map((a) => ({ ...a, read: true })))}>Mark all as read</button>
      </div>

      <div className="card update-list">
        {shown.map((a) => (
          <div key={a.id} className={`alert-row${a.read ? " read" : ""}`}>
            <span className={`status-dot ${a.level === "High" ? "high" : a.level === "Medium" ? "medium" : "low"}`} />
            <div className="update-main">
              <strong>{a.title}</strong>
              <small>{a.regulator} · {a.date}</small>
            </div>
            <span className={`impact ${a.level.toLowerCase()}`}>{a.level}</span>
            {!a.read && <button className="link-btn nomargin" onClick={() => markRead(a.id)}>Mark read</button>}
          </div>
        ))}
        {shown.length === 0 && <p className="muted">No alerts.</p>}
      </div>
    </div>
  );
}
