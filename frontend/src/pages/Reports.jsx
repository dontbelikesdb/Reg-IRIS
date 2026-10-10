import { Download, FileBarChart } from "lucide-react";
import { reports, impactMatrix, coverage, rules, alerts } from "../data/mockData.js";
import { downloadCsv } from "../services/export.js";

const builders = {
  impact: () => downloadCsv("impact-matrix.csv", ["Trade ID", "Product", "Regulator", "Rule", "Impact", "Reason"],
    impactMatrix.map((r) => [r.tradeId, r.product, r.regulator, r.rule, r.impact, r.reason])),
  coverage: () => downloadCsv("regulatory-coverage.csv", ["Regulator", "Documents"], coverage.map((c) => [c.regulator, c.docs])),
  rules: () => downloadCsv("rules-status.csv", ["Rule ID", "Regulator", "Name", "Severity", "Active"],
    rules.map((r) => [r.id, r.regulator, r.name, r.severity, r.active ? "Yes" : "No"])),
  alerts: () => downloadCsv("alerts-summary.csv", ["Title", "Regulator", "Level", "Date", "Status"],
    alerts.map((a) => [a.title, a.regulator, a.level, a.date, a.read ? "Read" : "Unread"])),
};

export default function Reports() {
  return (
    <div className="page-simple">
      <h1 className="page-title">Reports</h1>
      <p className="muted">Generate and download compliance reports as CSV.</p>

      <div className="report-grid">
        {reports.map((r) => (
          <div key={r.id} className="card report-card">
            <div className="round-icon green"><FileBarChart size={22} /></div>
            <h3>{r.title}</h3>
            <p className="muted">{r.desc}</p>
            <button className="btn" onClick={builders[r.id]}><Download size={15} /> Download CSV</button>
          </div>
        ))}
      </div>
    </div>
  );
}
