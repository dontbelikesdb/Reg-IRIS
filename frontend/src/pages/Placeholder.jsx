import { useLocation } from "react-router-dom";
import ImpactMatrix from "../components/ImpactMatrix.jsx";

const titles = {
  "/library": "Document Library", "/impact": "Impact Analysis", "/validator": "Trade Validator",
  "/alerts": "Alerts", "/reports": "Reports",
};

export default function Placeholder() {
  const { pathname } = useLocation();
  const title = titles[pathname] || "Page";
  return (
    <div className="page-simple">
      <h1 className="page-title">{title}</h1>
      {pathname === "/impact" ? (
        <div className="card"><ImpactMatrix /></div>
      ) : (
        <div className="card empty"><p className="muted">This section is coming soon.</p></div>
      )}
    </div>
  );
}
