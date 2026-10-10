import { Fragment, useMemo, useState } from "react";
import { ChevronDown, ChevronRight, ChevronUp, Download } from "lucide-react";
import "./ComplianceMatrix.css";

const PAGE_SIZE = 25;
const ruleKey = (regulatorId, ruleId) => `${regulatorId}:${ruleId}`;
const short = (text, n = 32) => (text.length > n ? `${text.slice(0, n - 1)}…` : text);

// Impact Matrix: one row per trade, one Pass/Fail column per rule, then the overall status.
// `report` is the JSON returned by POST /api/impact/check.
export default function ComplianceMatrix({ report, onExport, exporting = false }) {
  const rules = report.rules_checked;
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("ALL");
  const [sort, setSort] = useState({ key: "row", dir: "asc" });
  const [page, setPage] = useState(0);
  const [open, setOpen] = useState(null); // row_number of the expanded failed trade

  // Pre-compute which rules each trade failed (so a cell lookup is instant).
  const trades = useMemo(
    () => report.results.map((r) => ({ ...r, failed: new Set(r.violations.map((v) => ruleKey(v.regulator_id, v.rule_id))) })),
    [report],
  );

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = trades.filter((t) => (status === "ALL" || t.status === status) && (!q || t.trade_id.toLowerCase().includes(q)));
    const dir = sort.dir === "asc" ? 1 : -1;
    const by = {
      row: (a, b) => a.row_number - b.row_number,
      trade: (a, b) => a.trade_id.localeCompare(b.trade_id, undefined, { numeric: true }),
      status: (a, b) => a.status.localeCompare(b.status) || a.row_number - b.row_number, // FAIL sorts before PASS
    }[sort.key];
    return [...list].sort((a, b) => dir * by(a, b));
  }, [trades, query, status, sort]);

  const pageCount = Math.max(1, Math.ceil(visible.length / PAGE_SIZE));
  const current = Math.min(page, pageCount - 1);
  const rows = visible.slice(current * PAGE_SIZE, (current + 1) * PAGE_SIZE);
  const from = visible.length ? current * PAGE_SIZE + 1 : 0;

  const toggleSort = (key) => {
    setSort((s) => (s.key === key ? { key, dir: s.dir === "asc" ? "desc" : "asc" } : { key, dir: "asc" }));
    setPage(0);
  };
  const sortIcon = (k) => (sort.key === k ? (sort.dir === "asc" ? <ChevronUp size={13} /> : <ChevronDown size={13} />) : null);

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
              <th className="mx-sort" onClick={() => toggleSort("trade")}>Trade{sortIcon("trade")}</th>
              {rules.map((r) => (
                <th key={ruleKey(r.regulator_id, r.rule_id)} className="mx-rule-head" title={`${r.regulator_id} · ${r.description}`}>
                  {r.rule_id}: {short(r.description)}
                </th>
              ))}
              <th className="mx-sort" onClick={() => toggleSort("status")}>Overall{sortIcon("status")}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((t) => {
              const failed = t.status === "FAIL";
              const isOpen = open === t.row_number;
              return (
                <Fragment key={t.row_number}>
                  <tr className={`mx-row${failed ? " clickable" : ""}`} onClick={() => failed && setOpen(isOpen ? null : t.row_number)}>
                    <td className="mx-trade">
                      {failed ? (isOpen ? <ChevronDown size={15} /> : <ChevronRight size={15} />) : <span className="mx-spacer" />}
                      {t.trade_id}
                    </td>
                    {rules.map((r) => {
                      const bad = t.failed.has(ruleKey(r.regulator_id, r.rule_id));
                      return <td key={ruleKey(r.regulator_id, r.rule_id)} className={`mx-cell${bad ? " fail" : ""}`}>{bad ? "Fail" : "Pass"}</td>;
                    })}
                    <td><span className={`pill mx-pill ${failed ? "red" : "green"}`}>{t.status}</span></td>
                  </tr>
                  {isOpen && (
                    <tr className="mx-detail">
                      <td colSpan={rules.length + 2}>
                        <ul>
                          {t.violations.map((v) => (
                            <li key={ruleKey(v.regulator_id, v.rule_id)}>
                              <div><strong>{v.rule_id}</strong> <span className="sub">({v.regulator}) · {v.description}</span></div>
                              <div className="why">{v.explanation}</div>
                              <div className="sub">
                                {v.impact}
                                {Object.keys(v.evidence).length > 0 && (
                                  <> · Values checked: {Object.entries(v.evidence).map(([k, val]) => `${k} = ${val ?? "empty"}`).join(", ")}</>
                                )}
                              </div>
                            </li>
                          ))}
                        </ul>
                      </td>
                    </tr>
                  )}
                </Fragment>
              );
            })}
            {!rows.length && <tr><td colSpan={rules.length + 2} className="muted">No trades match.</td></tr>}
          </tbody>
        </table>
      </div>

      <div className="mx-pager">
        <span>Showing {from}–{Math.min((current + 1) * PAGE_SIZE, visible.length)} of {visible.length} trades · click a failed row to see why</span>
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