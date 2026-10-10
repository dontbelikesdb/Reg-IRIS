import { useRef, useState } from "react";
import { Upload, Download, Play } from "lucide-react";
import { sampleTrades, regulators, counterpartyTypes } from "../data/mockData.js";
import { downloadCsv } from "../services/export.js";

const FIELD_ALIASES = {
  tradeid: "tradeId", producttype: "product", product: "product", regulator: "regulator",
  ruleclause: "rule", rule: "rule", clause: "rule", price: "price",
  notionalcurrency: "notionalCurrency", currency: "notionalCurrency",
  counterpartytype: "counterparty", counterparty: "counterparty", uti: "uti",
};

function splitLine(line) {
  const out = []; let cur = ""; let quoted = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (c === '"') { if (quoted && line[i + 1] === '"') { cur += '"'; i++; } else quoted = !quoted; }
    else if (c === "," && !quoted) { out.push(cur.trim()); cur = ""; }
    else cur += c;
  }
  out.push(cur.trim());
  return out;
}

function parseCsv(text) {
  const lines = text.split(/\r?\n/).filter((l) => l.trim());
  if (lines.length < 2) return [];
  const keys = splitLine(lines[0]).map((h) => FIELD_ALIASES[h.toLowerCase().replace(/[^a-z]/g, "")]);
  return lines.slice(1).map((line, i) => {
    const cells = splitLine(line);
    const row = { tradeId: `TDR${String(i + 1).padStart(3, "0")}`, product: "", regulator: "", rule: "", price: "", notionalCurrency: "", counterparty: "", uti: "" };
    keys.forEach((k, idx) => { if (k) row[k] = cells[idx] ?? ""; });
    return row;
  });
}

function evaluate(t) {
  const issues = [];
  if (!t.price) issues.push("Price field missing");
  if (!t.uti) issues.push("UTI not generated");
  if (!t.notionalCurrency) issues.push("Missing notional currency");
  if (!counterpartyTypes.includes(t.counterparty)) issues.push("Invalid counterparty type");
  return issues.length
    ? { status: "Fail", reason: issues.join("; ") }
    : { status: "Pass", reason: t.regulator === "FCA" ? "Reporting within threshold" : "All checks passed" };
}

export default function ImpactAnalysis() {
  const [trades, setTrades] = useState(sampleTrades);
  const [selected, setSelected] = useState(regulators);
  const [results, setResults] = useState({});
  const [fileName, setFileName] = useState("");
  const [error, setError] = useState("");
  const fileRef = useRef(null);

  const toggle = (r) => setSelected((s) => (s.includes(r) ? s.filter((x) => x !== r) : [...s, r]));
  const shown = trades.filter((t) => selected.includes(t.regulator));

  const onUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const rows = parseCsv(await file.text());
    e.target.value = "";
    if (!rows.length) { setError("Could not read any rows. Check the CSV has a header row and data."); return; }
    setError(""); setFileName(file.name); setTrades(rows); setResults({});
    const found = [...new Set(rows.map((r) => r.regulator).filter(Boolean))];
    if (found.length) setSelected(regulators.filter((r) => found.includes(r)));
  };

  const runEvaluate = () => {
    const next = {};
    shown.forEach((t) => { next[t.tradeId] = evaluate(t); });
    setResults(next);
  };

  const exportCsv = () =>
    downloadCsv("impact-analysis.csv", ["Trade ID", "Product Type", "Regulator", "Rule / Clause", "Status", "Reason"],
      shown.map((t) => [t.tradeId, t.product, t.regulator, t.rule, results[t.tradeId]?.status ?? "Pending", results[t.tradeId]?.reason ?? ""]));

  const downloadTemplate = () =>
    downloadCsv("trades-template.csv", ["Trade ID", "Product Type", "Regulator", "Rule / Clause", "Price", "Notional Currency", "Counterparty Type", "UTI"],
      [["TDR100", "Interest Rate Swap", "EMIR", "Rule 4.2", "101.25", "EUR", "Financial", "UTI100"]]);

  return (
    <div className="page-simple wide-page">
      <h1 className="page-title">Impact Analysis</h1>
      <p className="muted">Upload trades, choose regulators and evaluate them against the rules.</p>

      <div className="card">
        <div className="toolbar-row nomt">
          <div>
            <input ref={fileRef} type="file" accept=".csv" hidden onChange={onUpload} />
            <button className="btn" onClick={() => fileRef.current.click()}><Upload size={15} /> Upload CSV</button>
            <button className="link-btn tpl" onClick={downloadTemplate}>Download template</button>
            {fileName && <span className="muted file-name">{fileName}</span>}
          </div>
        </div>
        {error && <p className="error-text">{error}</p>}

        <p className="small label">Choose Regulator</p>
        <div className="check-row">
          {regulators.map((r) => (
            <label key={r} className="check">
              <input type="checkbox" checked={selected.includes(r)} onChange={() => toggle(r)} /> {r}
            </label>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="card-title">
          <h2>Impact Matrix (Trade ↔ Rule)</h2>
          <button className="btn" onClick={runEvaluate} disabled={!shown.length}><Play size={14} /> Evaluate</button>
        </div>
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr><th>Trade ID</th><th>Product Type</th><th>Regulator</th><th>Rule / Clause</th><th>Status</th><th>Reason</th></tr>
            </thead>
            <tbody>
              {shown.map((t) => {
                const r = results[t.tradeId];
                return (
                  <tr key={t.tradeId}>
                    <td>{t.tradeId}</td><td>{t.product}</td><td>{t.regulator}</td><td>{t.rule}</td>
                    <td>{r ? <span className={`impact ${r.status === "Pass" ? "low" : "high"}`}>{r.status}</span> : <span className="impact pending">Pending</span>}</td>
                    <td>{r?.reason ?? "—"}</td>
                  </tr>
                );
              })}
              {!shown.length && <tr><td colSpan="6" className="muted">No trades for the selected regulators.</td></tr>}
            </tbody>
          </table>
        </div>
        <div className="card-footer">
          <button className="btn" onClick={exportCsv} disabled={!shown.length}><Download size={15} /> Export CSV</button>
        </div>
      </div>
    </div>
  );
}
