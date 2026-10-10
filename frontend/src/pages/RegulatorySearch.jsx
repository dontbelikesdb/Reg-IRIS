import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Search } from "lucide-react";
import SearchResultCard from "../components/SearchResultCard.jsx";
import CitationDialog from "../components/CitationDialog.jsx";
import { searchDocuments } from "../services/api.js";
import { popularSearches } from "../data/mockData.js";

export default function RegulatorySearch() {
  const [params, setParams] = useSearchParams();
  const initial = params.get("q") || "";
  const [q, setQ] = useState(initial);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [cite, setCite] = useState(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    searchDocuments(initial).then((r) => { if (active) { setResults(r); setLoading(false); } });
    return () => { active = false; };
  }, [initial]);

  const submit = (e) => { e.preventDefault(); setParams(q ? { q } : {}); };

  return (
    <div className="page-simple">
      <h1 className="page-title">Regulatory Search</h1>
      <p className="muted">Search across regulatory documents, rules and clauses.</p>

      <form className="search-box wide" onSubmit={submit}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ask a regulatory question..." />
        <button className="btn icon-only" aria-label="Search"><Search size={18} /></button>
      </form>
      <div className="chip-row">
        {popularSearches.map((p) => <button key={p} className="chip" onClick={() => { setQ(p); setParams({ q: p }); }}>{p}</button>)}
      </div>

      <div className="result-list">
        {loading ? <p className="muted">Searching…</p>
          : results.length === 0 ? <p className="muted">No results found.</p>
          : results.map((r) => <SearchResultCard key={r.id} result={r} onCite={setCite} />)}
      </div>

      <CitationDialog open={Boolean(cite)} title="Citation" onClose={() => setCite(null)}>
        {cite && <><strong>{cite.title}</strong><p>{cite.citation}</p></>}
      </CitationDialog>
    </div>
  );
}
