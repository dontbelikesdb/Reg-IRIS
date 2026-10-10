import { useState } from "react";
import WhatsNewCard from "../components/WhatsNewCard.jsx";
import CitationDialog from "../components/CitationDialog.jsx";
import { updates } from "../data/mockData.js";

export default function WhatsNew() {
  const [selected, setSelected] = useState(null);
  return (
    <div className="page-simple">
      <h1 className="page-title">What's New</h1>
      <p className="muted">Review regulatory updates and their version changes.</p>

      <div className="card update-list">
        {updates.map((u) => <WhatsNewCard key={u.id} item={u} onOpen={setSelected} />)}
      </div>

      <CitationDialog open={Boolean(selected)} title={selected?.title} onClose={() => setSelected(null)}>
        {selected && (
          <>
            <p className="muted">{selected.regulator} · {selected.date}</p>
            <strong>Version comparison</strong>
            <ul>{selected.changes.map((c) => <li key={c}>{c}</li>)}</ul>
          </>
        )}
      </CitationDialog>
    </div>
  );
}
