import { useMemo, useState } from "react";
import { ChevronDown, ChevronUp, Download } from "lucide-react";
import "./ComplianceMatrix.css";

const PAGE_SIZE = 25;

// Impact Matrix: Trade_ID | one Pass/Fail column per selected regulator | Violations | Impact Explanation.
export default function ComplianceMatrix({ report, onExport, exporting = false }) {
  const regulators = useMemo(() => {
    const names = Object.fromEntries(report.summary.by_regulator.map((s) => [s.regulator_id, s.name]));
    return report.regulators_checked.map((id) => ({ id, name: names[id] ?? id }));
  }, [report]);

  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("ALL");
  const [sortDir, setSortDir] = useState("asc"); // "asc" keeps the original file order
  const [page, setPage] = useState(0);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = report.results.filter((t) => (status === "ALL" || t.status === status) && (!q || t.trade_id.toLowerCase().includes(q)));
    return sortDir === "asc"
      ? list
      : [...list].sort((a, b) => b.trade_id.localeCompare(a.trade_id, undefined, { numeric: true }));
  }, [report, query, status, sortDir]);

  const pageCount = Math.max(1, Math.ceil(visible.length / PAGE_SIZE));
  const current = Math.min(page, pageCount - 1);
  const rows = visible.slice(current * PAGE_SIZE, (current + 1) * PAGE_SIZE);
  const from = visible.length ? current * PAGE_SIZE + 1 : 0;
  const columnCount = regulators.length + 3;

  return (
    <>
      <div className="mx-toolbar">
        <input
          className="mx-search"
          placeholder="Search Trade ID…"
          value={query}
          onChange={(e) => { setQuery(e.target.value); setPage(0); }}
        />
        <select className="mx-select" value={status} onChange={(e) => { setStatus(e.target.value); setPage(0); }}>
          <option value="ALL">All trades</option>
          <option value="FAIL">Failed only</option>
          <option value="PASS">Passed only</option>
        </select>
      </div>

      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th className="mx-sort" onClick={() => { setSortDir(sortDir === "asc" ? "desc" : "asc"); setPage(0); }}>
                Trade_ID{sortDir === "asc" ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
              </th>
              {regulators.map((r) => <th key={r.id}>{r.name}</th>)}
              <th>Violations</th>
              <th>Impact Explanation</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((t) => (
              <tr key={t.row_number} className="mx-row">
                <td className="mx-trade">{t.trade_id}</td>
                {regulators.map((r) => {
                  const bad = t.regulator_status[r.id] !== "PASS";
                  return <td key={r.id} className={`mx-cell${bad ? " fail" : ""}`}>{bad ? "Fail" : "Pass"}</td>;
                })}
                <td className="mx-violations">
                  {t.violations.length
                    ? t.violations.map((v) => (
                        <span key={`${v.regulator_id}:${v.rule_id}`} className="pill red mx-rule-pill" title={`${v.regulator} · ${v.description}`}>{v.rule_id}</span>
                      ))
                    : <span className="muted">—</span>}
                </td>
                <td className="mx-explain">
                  {t.violations.length
                    ? t.violations.map((v) => (
                        <p key={`${v.regulator_id}:${v.rule_id}`}><strong>{v.rule_id}:</strong> {v.explanation}</p>
                      ))
                    : <span className="muted">—</span>}
                </td>
              </tr>
            ))}
            {!rows.length && <tr><td colSpan={columnCount} className="muted">No trades match.</td></tr>}
          </tbody>
        </table>
      </div>

      <div className="mx-pager">
        <span>Showing {from}–{Math.min((current + 1) * PAGE_SIZE, visible.length)} of {visible.length} trades</span>
        <div className="mx-pager-btns">
          <button className="btn ghost" disabled={current === 0} onClick={() => setPage(current - 1)}>Previous</button>
          <span>Page {current + 1} / {pageCount}</span>
          <button className="btn ghost" disabled={current >= pageCount - 1} onClick={() => setPage(current + 1)}>Next</button>
          <button className="btn" onClick={onExport} disabled={exporting}><Download size={15} /> {exporting ? "Preparing…" : "Export CSV"}</button>
        </div>
      </div>
    </>
  );
}