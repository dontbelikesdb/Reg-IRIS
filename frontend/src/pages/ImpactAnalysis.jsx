import { useEffect, useRef, useState } from "react";
import { FileJson, Play, Upload, X } from "lucide-react";
import ComplianceMatrix from "../components/ComplianceMatrix.jsx";
import { checkTrades, exportReportCsv, fetchRegulators, validateRuleFile } from "../services/ruleEngine.js";
import { downloadCsv, downloadJson } from "../services/export.js";

const TEMPLATE_HEADERS = ["Trade_ID", "Asset_Class", "Timestamp", "Counterparty_LEI", "Price", "Quantity", "Currency", "Maturity_Date", "Underlying_ISIN"];
const TEMPLATE_ROW = ["T000001", "Derivative", "2024-06-25T09:15:00Z", "5493001KJTI42S8N5L34", "105.4", "500", "USD", "2030-01-01", "US0378331005"];

// Shown by "Rule template": the format a custom regulator file must follow (save it as rules_<name>.json).
const RULES_TEMPLATE = {
  regulator: "My Regulator",
  jurisdiction: "EU",
  rules: [
    {
      id: "MYREG-1",
      description: "All derivatives must include a valid Underlying_ISIN.",
      logic: {
        and: [
          { "==": [{ var: "Asset_Class" }, "Derivative"] },
          { var: "Underlying_ISIN" },
          { regex: ["Underlying_ISIN", "^[A-Z0-9]{12}$"] },
        ],
      },
      impact: "Derivative trades need a valid ISIN for the underlying instrument.",
    },
    {
      id: "MYREG-2",
      description: "Quantity must be a positive number.",
      logic: { ">": [{ var: "Quantity" }, 0] },
      impact: "Quantity cannot be zero or negative.",
    },
  ],
};

export default function ImpactAnalysis() {
  const [regulators, setRegulators] = useState([]); // from GET /api/regulators
  const [custom, setCustom] = useState([]); // user-uploaded rule files: { ...regulatorInfo, file }
  const [selected, setSelected] = useState([]);
  const [file, setFile] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [checkingRules, setCheckingRules] = useState(false);
  const [error, setError] = useState("");
  const fileRef = useRef(null);
  const rulesRef = useRef(null);

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

  // Each picked rules_<name>.json is validated by the server, then kept in memory (nothing is saved server-side).
  const onPickRuleFiles = async (e) => {
    const picked = Array.from(e.target.files || []);
    e.target.value = "";
    if (!picked.length) return;
    setCheckingRules(true);
    setError("");
    const problems = [];
    for (const f of picked) {
      try {
        const info = await validateRuleFile(f);
        setCustom((list) => [...list.filter((c) => c.id !== info.id), { ...info, file: f }]);
        setSelected((s) => (s.includes(info.id) ? s : [...s, info.id]));
      } catch (err) {
        problems.push(err.message.includes(f.name) ? err.message : `${f.name}: ${err.message}`); // server messages already name the file
      }
    }
    setCheckingRules(false);
    setError(problems.join("\n"));
  };

  const removeCustom = (id) => {
    setCustom((list) => list.filter((c) => c.id !== id));
    setSelected((s) => s.filter((x) => x !== id));
  };

  const runCheck = async () => {
    setLoading(true);
    setError("");
    try {
      const customIds = new Set(custom.map((c) => c.id));
      const builtIn = selected.filter((id) => !customIds.has(id));
      const ruleFiles = custom.filter((c) => selected.includes(c.id)).map((c) => c.file);
      setReport(await checkTrades(file, builtIn, ruleFiles));
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

        <div className="label-row">
          <p className="small label">Choose Regulator</p>
          <input ref={rulesRef} type="file" accept=".json,application/json" multiple hidden onChange={onPickRuleFiles} />
          <button className="btn ghost sm" onClick={() => rulesRef.current.click()} disabled={checkingRules}>
            <FileJson size={14} /> {checkingRules ? "Checking…" : "Upload regulator JSON"}
          </button>
          <button className="link-btn tpl" onClick={() => downloadJson("rules_myregulator.json", RULES_TEMPLATE)}>Rule template</button>
        </div>
        <div className="check-row">
          {[...regulators, ...custom].map((r) => (
            <label key={r.id} className="check">
              <input type="checkbox" checked={selected.includes(r.id)} onChange={() => toggle(r.id)} /> {r.name}
              <span className="muted">· {r.rule_count} rules</span>
              {r.file && (
                <>
                  <span className="tag">custom</span>
                  <button
                    type="button"
                    className="chip-x"
                    title={`Remove ${r.file.name}`}
                    aria-label={`Remove ${r.name}`}
                    onClick={(e) => { e.preventDefault(); removeCustom(r.id); }}
                  >
                    <X size={13} />
                  </button>
                </>
              )}
            </label>
          ))}
          {!regulators.length && !custom.length && !error && <span className="muted">Loading regulators…</span>}
        </div>
        <p className="muted rule-hint">
          Have your own rules? Upload a file named <code>rules_&lt;regulatorName&gt;.json</code>. It is checked on upload and used only for this session.
        </p>
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