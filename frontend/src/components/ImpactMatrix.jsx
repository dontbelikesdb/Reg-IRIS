import { Download } from "lucide-react";
import { impactMatrix } from "../data/mockData.js";

const toCsv = (rows) => {
  const head = ["Trade ID", "Product Type", "Regulator", "Rule / Clause", "Impact", "Reason"];
  const body = rows.map((r) => [r.tradeId, r.product, r.regulator, r.rule, r.impact, r.reason].map((v) => `"${v}"`).join(","));
  return [head.join(","), ...body].join("\n");
};

export default function ImpactMatrix({ rows = impactMatrix }) {
  const exportCsv = () => {
    const url = URL.createObjectURL(new Blob([toCsv(rows)], { type: "text/csv" }));
    const a = Object.assign(document.createElement("a"), { href: url, download: "impact-matrix.csv" });
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr><th>Trade ID</th><th>Product Type</th><th>Regulator</th><th>Rule / Clause</th><th>Impact</th><th>Reason</th></tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.tradeId}>
                <td>{r.tradeId}</td><td>{r.product}</td><td>{r.regulator}</td><td>{r.rule}</td>
                <td><span className={`impact ${r.impact.toLowerCase()}`}>{r.impact}</span></td>
                <td>{r.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="card-footer">
        <button className="btn" onClick={exportCsv}><Download size={15} /> Export CSV</button>
      </div>
    </>
  );
}
