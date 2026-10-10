import { NavLink } from "react-router-dom";
import { LayoutDashboard, Search, FileText, Bell, BarChart3, ShieldCheck, Settings, AlertTriangle, ClipboardList } from "lucide-react";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/search", label: "Regulatory Search", icon: Search },
  { to: "/library", label: "Document Library", icon: FileText },
  { to: "/updates", label: "What's New", icon: Bell },
  { to: "/impact", label: "Impact Analysis", icon: BarChart3 },
  { to: "/validator", label: "Trade Validator", icon: ShieldCheck },
  { to: "/rule-engine", label: "Rules Engine", icon: Settings },
  { to: "/alerts", label: "Alerts", icon: AlertTriangle },
  { to: "/reports", label: "Reports", icon: ClipboardList },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} end={to === "/"} className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>
            <Icon size={18} /> {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
