import { useEffect, useRef, useState } from "react";
import { Play, Upload } from "lucide-react";
import ComplianceMatrix from "../components/ComplianceMatrix.jsx";
import { checkTrades, exportReportCsv, fetchRegulators } from "../services/ruleEngine.js";
import { downloadCsv } from "../services/export.js";

const TEMPLATE_HEADERS = ["Trade_ID", "Asset_Class", "Timestamp", "Counterparty_LEI", "Price", "Quantity", "Currency", "Maturity_Date", "Underlying_ISIN"];
const TEMPLATE_ROW = ["T000001", "Derivative", "2024-06-25T09:15:00Z", "5493001KJTI42S8N5L34", "105.4", "500", "USD", "2030-01-01", "US0378331005"];

export default function ImpactAnalysis() {
  const [regulators, setRegulators] = useState([]); // from GET /api/regulators
  const [selected, setSelected] = useState([]);
  const [file, setFile] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef(null);

  useEffect(() => {
    let cancelled = false;
    fetchRegulators()
      .then((list) => {
        if (cancelled) return;
        setRegulators(list);
        setSelected(list.map((r) => r.id));
      })
      .catch((e) => !cancelled && setError(e.message));
    return () => { cancelled = true; };
  }, []);

  const toggle = (id) => setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));

  const onPickFile = (e) => {
    const picked = e.target.files?.[0];
    e.target.value = ""; // lets the same file be picked again
    if (!picked) return;
    setFile(picked);
    setReport(null);
    setError("");
  };

  const runCheck = async () => {
    setLoading(true);
    setError("");
    try {
      setReport(await checkTrades(file, selected));
    } catch (e) {
      setReport(null);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const exportCsv = async () => {
    setExporting(true);
    try {
      await exportReportCsv(report);
    } catch (e) {
      setError(e.message);
    } finally {
      setExporting(false);
    }
  };

  const s = report?.summary;

  return (
    <div className="page-simple wide-page mx-page">
      <h1 className="page-title">Impact Analysis</h1>
      <p className="muted">Upload trades, choose regulators and see which trades pass or fail each rule.</p>

      <div className="card">
        <div className="toolbar-row nomt">
          <div>
            <input ref={fileRef} type="file" accept=".csv" hidden onChange={onPickFile} />
            <button className="btn" onClick={() => fileRef.current.click()}><Upload size={15} /> Upload CSV</button>
            <button className="link-btn tpl" onClick={() => downloadCsv("trades-template.csv", TEMPLATE_HEADERS, [TEMPLATE_ROW])}>Download template</button>
            {file && <span className="muted file-name">{file.name}</span>}
          </div>
        </div>

        <p className="small label">Choose Regulator</p>
        <div className="check-row">
          {regulators.map((r) => (
            <label key={r.id} className="check">
              <input type="checkbox" checked={selected.includes(r.id)} onChange={() => toggle(r.id)} /> {r.name}
              <span className="muted">· {r.rule_count} rules</span>
            </label>
          ))}
          {!regulators.length && !error && <span className="muted">Loading regulators…</span>}
        </div>
        {error && <p className="error-text">{error}</p>}
      </div>

      <div className="card">
        <div className="card-title">
          <h2>Impact Matrix (Trade ↔ Rule)</h2>
          <button className="btn" onClick={runCheck} disabled={!file || !selected.length || loading}>
            <Play size={14} /> {loading ? "Evaluating…" : "Evaluate"}
          </button>
        </div>

        {!report && <p className="muted">{file ? "Ready — press Evaluate." : "Upload a trades CSV to get started."}</p>}

        {report && (
          <>
            <div className="mx-summary">
              <div><strong>{s.total_trades}</strong><span>Trades checked</span></div>
              <div className="good"><strong>{s.passed}</strong><span>Passed</span></div>
              <div className="bad"><strong>{s.failed}</strong><span>Failed</span></div>
              <div><strong>{s.pass_rate}%</strong><span>Pass rate</span></div>
            </div>
            {report.warnings.length > 0 && (
              <div className="mx-warn">{report.warnings.map((w) => <p key={w}>{w}</p>)}</div>
            )}
            <ComplianceMatrix report={report} onExport={exportCsv} exporting={exporting} />
          </>
        )}
      </div>
    </div>
  );
}