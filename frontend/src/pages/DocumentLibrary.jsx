import { useRef, useState } from "react";
import { Upload, Search } from "lucide-react";
import { documents as initial, regulators } from "../data/mockData.js";

export default function DocumentLibrary() {
  const [docs, setDocs] = useState(initial);
  const [filter, setFilter] = useState("All");
  const [q, setQ] = useState("");
  const [uploadReg, setUploadReg] = useState(regulators[0]);
  const fileRef = useRef(null);

  const onUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const ext = file.name.split(".").pop().toUpperCase();
    setDocs((d) => [
      { id: Date.now(), name: file.name.replace(/\.[^.]+$/, ""), regulator: uploadReg, type: ext, version: "v1",
        date: new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }) },
      ...d,
    ]);
    e.target.value = "";
  };

  const shown = docs.filter(
    (d) => (filter === "All" || d.regulator === filter) && d.name.toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div className="page-simple">
      <h1 className="page-title">Document Library</h1>
      <p className="muted">Browse and upload regulatory documents.</p>

      <div className="card toolbar">
        <div className="search-box grow">
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search documents..." />
          <span className="search-icon"><Search size={16} /></span>
        </div>
        <select className="select" value={uploadReg} onChange={(e) => setUploadReg(e.target.value)} aria-label="Regulator for upload">
          {regulators.map((r) => <option key={r}>{r}</option>)}
        </select>
        <input ref={fileRef} type="file" accept=".pdf,.html,.txt" hidden onChange={onUpload} />
        <button className="btn" onClick={() => fileRef.current.click()}><Upload size={15} /> Upload</button>
      </div>

      <div className="chip-row filters">
        {["All", ...regulators].map((r) => (
          <button key={r} className={`chip${filter === r ? " active" : ""}`} onClick={() => setFilter(r)}>{r}</button>
        ))}
      </div>

      <div className="card">
        <div className="table-wrap">
          <table className="table">
            <thead><tr><th>Document</th><th>Regulator</th><th>Type</th><th>Version</th><th>Date</th></tr></thead>
            <tbody>
              {shown.map((d) => (
                <tr key={d.id}>
                  <td>{d.name}</td><td><span className="tag">{d.regulator}</span></td>
                  <td>{d.type}</td><td>{d.version}</td><td>{d.date}</td>
                </tr>
              ))}
              {shown.length === 0 && <tr><td colSpan="5" className="muted">No documents found.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
