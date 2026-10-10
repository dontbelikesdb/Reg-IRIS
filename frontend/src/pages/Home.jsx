import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Search } from "lucide-react";
import StatCard from "../components/StatCard.jsx";
import WhatsNewCard from "../components/WhatsNewCard.jsx";
import FeatureCard from "../components/FeatureCard.jsx";
import ImpactMatrix from "../components/ImpactMatrix.jsx";
import CoverageChart from "../components/CoverageChart.jsx";
import AssistantPanel from "../components/AssistantPanel.jsx";
import CitationDialog from "../components/CitationDialog.jsx";
import { stats, updates, popularSearches, documentActions } from "../data/mockData.js";

export default function Home() {
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState(null);
  const navigate = useNavigate();
  const go = (term) => navigate(`/search?q=${encodeURIComponent(term)}`);

  return (
    <div className="home">
      <section className="welcome">
        <h1>Welcome back, Priya!</h1>
        <p>Stay ahead of regulatory changes, search with intelligence and assess the impact on your trades — all in one place.</p>
      </section>

      <section className="stat-grid">
        {stats.map((s) => <StatCard key={s.id} {...s} />)}
      </section>

      <section className="grid-2">
        <div className="card">
          <div className="card-title"><h2>What's New</h2><Link to="/updates">View All</Link></div>
          <div className="update-list">
            {updates.slice(0, 3).map((u) => <WhatsNewCard key={u.id} item={u} onOpen={setSelected} />)}
          </div>
        </div>

        <div className="stack">
          <div className="card">
            <div className="card-title"><h2>Search Regulatory Documents</h2><Link to="/search">Advanced Search</Link></div>
            <form className="search-box" onSubmit={(e) => { e.preventDefault(); go(q); }}>
              <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="E.g. What are the reporting requirements for interest rate swaps under EMIR?" />
              <button className="btn icon-only" aria-label="Search"><Search size={18} /></button>
            </form>
            <p className="muted small">Popular searches</p>
            <div className="chip-row">
              {popularSearches.map((p) => <button key={p} className="chip" onClick={() => go(p)}>{p}</button>)}
            </div>
          </div>

          <div className="card">
            <div className="card-title"><h2>Document Library</h2><Link to="/library">View All</Link></div>
            <div className="tile-grid">
              {documentActions.map((a) => <FeatureCard key={a.id} {...a} />)}
            </div>
          </div>
        </div>
      </section>

      <section className="grid-3">
        <div className="card">
          <div className="card-title"><h2>Impact Matrix (Trade ↔ Rule)</h2><Link to="/impact">View All</Link></div>
          <ImpactMatrix />
        </div>

        <div className="stack">
          <div className="card">
            <div className="card-title"><h2>Regulatory Coverage</h2></div>
            <CoverageChart />
          </div>
          <AssistantPanel />
        </div>
      </section>

      <CitationDialog open={Boolean(selected)} title={selected?.title} onClose={() => setSelected(null)}>
        {selected && (
          <>
            <p className="muted">{selected.regulator} · {selected.date}</p>
            <p>{selected.summary}</p>
            <ul>{selected.changes.map((c) => <li key={c}>{c}</li>)}</ul>
          </>
        )}
      </CitationDialog>
    </div>
  );
}
