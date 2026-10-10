import { useState } from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import { productTypes, regulators, counterpartyTypes } from "../data/mockData.js";

const empty = { tradeId: "", product: productTypes[0], regulator: regulators[0], price: "", notionalCurrency: "", counterparty: "", uti: "" };

function validate(t) {
  const issues = [];
  if (!t.price) issues.push({ level: "High", rule: "EMIR Rule 4.2", msg: "Price field missing" });
  if (!t.uti) issues.push({ level: "High", rule: "Dodd-Frank Section 723", msg: "UTI not generated" });
  if (!t.notionalCurrency) issues.push({ level: "Medium", rule: "EMIR Rule 4.3", msg: "Missing notional currency" });
  if (!t.counterparty) issues.push({ level: "Medium", rule: "MiFID II RTS 22.5", msg: "Invalid counterparty type" });
  return issues;
}

export default function TradeValidator() {
  const [trade, setTrade] = useState(empty);
  const [result, setResult] = useState(null);
  const set = (k) => (e) => setTrade((t) => ({ ...t, [k]: e.target.value }));

  return (
    <div className="page-simple">
      <h1 className="page-title">Trade Validator</h1>
      <p className="muted">Check a trade against regulatory rules.</p>

      <form className="card form-grid" onSubmit={(e) => { e.preventDefault(); setResult(validate(trade)); }}>
        <label>Trade ID<input value={trade.tradeId} onChange={set("tradeId")} placeholder="TDR006" /></label>
        <label>Product Type
          <select className="select" value={trade.product} onChange={set("product")}>{productTypes.map((p) => <option key={p}>{p}</option>)}</select>
        </label>
        <label>Regulator
          <select className="select" value={trade.regulator} onChange={set("regulator")}>{regulators.map((r) => <option key={r}>{r}</option>)}</select>
        </label>
        <label>Price<input value={trade.price} onChange={set("price")} placeholder="e.g. 101.25" /></label>
        <label>Notional Currency<input value={trade.notionalCurrency} onChange={set("notionalCurrency")} placeholder="e.g. EUR" /></label>
        <label>Counterparty Type
          <select className="select" value={trade.counterparty} onChange={set("counterparty")}>
            <option value="">Select…</option>{counterpartyTypes.map((c) => <option key={c}>{c}</option>)}
          </select>
        </label>
        <label>UTI<input value={trade.uti} onChange={set("uti")} placeholder="Unique transaction identifier" /></label>
        <div className="form-actions">
          <button type="button" className="btn ghost" onClick={() => { setTrade(empty); setResult(null); }}>Reset</button>
          <button className="btn">Validate</button>
        </div>
      </form>

      {result && (
        <div className="card">
          {result.length === 0 ? (
            <div className="result ok"><CheckCircle2 size={20} /> No issues found. Trade passes all checks.</div>
          ) : (
            <>
              <div className="result bad"><XCircle size={20} /> {result.length} issue{result.length > 1 ? "s" : ""} found</div>
              <div className="table-wrap">
                <table className="table">
                  <thead><tr><th>Impact</th><th>Rule</th><th>Reason</th></tr></thead>
                  <tbody>
                    {result.map((i) => (
                      <tr key={i.msg}><td><span className={`impact ${i.level.toLowerCase()}`}>{i.level}</span></td><td>{i.rule}</td><td>{i.msg}</td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
