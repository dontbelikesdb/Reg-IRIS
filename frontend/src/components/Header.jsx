import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Sparkles, Bell, ChevronDown } from "lucide-react";
import { user } from "../data/mockData.js";

export default function Header() {
  const [q, setQ] = useState("");
  const navigate = useNavigate();
  const submit = (e) => {
    e.preventDefault();
    navigate(`/search${q ? `?q=${encodeURIComponent(q)}` : ""}`);
  };

  return (
    <header className="top-header">
      <div className="brand">
        <div className="brand-mark">BNP<br />PARIBAS</div>
        <div className="brand-divider" />
        <div>
          <h1>Reg <span>IRIS</span></h1>
          <p>Intelligent Regulatory Repository & Impact Scanner</p>
        </div>
      </div>

      <form className="header-search" onSubmit={submit}>
        <Search size={16} />
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Ask a regulatory question..." />
        <Sparkles size={16} className="spark" />
      </form>

      <div className="header-actions">
        <button className="icon-btn" aria-label="Notifications">
          <Bell size={19} /><span className="dot" />
        </button>
        <div className="profile">
          <div className="avatar">{user.initials}</div>
          <span>{user.name}</span>
          <ChevronDown size={15} />
        </div>
      </div>
    </header>
  );
}
