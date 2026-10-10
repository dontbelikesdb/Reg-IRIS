import { coverage } from "../data/mockData.js";

export default function CoverageChart() {
  const max = Math.max(...coverage.map((c) => c.docs));
  return (
    <div className="coverage">
      {coverage.map((c) => (
        <div key={c.regulator} className="cov-row">
          <span>{c.regulator}</span>
          <div className="cov-track"><div className="cov-bar" style={{ width: `${(c.docs / max) * 100}%` }} /></div>
          <strong>{c.docs}</strong>
        </div>
      ))}
    </div>
  );
}
