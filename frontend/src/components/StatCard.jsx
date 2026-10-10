import { FileText, Bell, ScrollText, Activity } from "lucide-react";

const icons = { file: FileText, bell: Bell, rules: ScrollText, activity: Activity };

export default function StatCard({ value, label, note, tone, icon }) {
  const Icon = icons[icon] || FileText;
  return (
    <div className="card stat-card">
      <div className={`round-icon ${tone}`}><Icon size={22} /></div>
      <div>
        <strong>{value}</strong>
        <span>{label}</span>
        <em className={`pill ${tone}`}>{note}</em>
      </div>
    </div>
  );
}
