export default function SearchResultCard({ result, onCite }) {
  return (
    <article className="card result-card">
      <div className="result-top">
        <span className="tag">{result.regulator}</span>
        <small>{result.clause} · {result.date}</small>
      </div>
      <h3>{result.title}</h3>
      <p>{result.snippet}</p>
      <button className="link-btn" onClick={() => onCite(result)}>View citation</button>
    </article>
  );
}
