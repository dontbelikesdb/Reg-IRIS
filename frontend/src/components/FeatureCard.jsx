import { Link } from "react-router-dom";
import { Upload, FileText, Clock, Settings } from "lucide-react";

const icons = { upload: Upload, file: FileText, clock: Clock, settings: Settings };

export default function FeatureCard({ title, sub, icon, tone, to }) {
  const Icon = icons[icon] || FileText;
  return (
    <Link to={to} className={`feature-tile ${tone}`}>
      <Icon size={22} />
      <strong>{title}</strong>
      <span>{sub}</span>
    </Link>
  );
}
