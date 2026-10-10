import { X } from "lucide-react";

export default function CitationDialog({ open, title, children, onClose }) {
  if (!open) return null;
  return (
    <div className="overlay" onClick={onClose}>
      <div className="dialog" onClick={(e) => e.stopPropagation()}>
        <div className="dialog-head">
          <h3>{title}</h3>
          <button className="icon-btn" onClick={onClose} aria-label="Close"><X size={18} /></button>
        </div>
        <div className="dialog-body">{children}</div>
      </div>
    </div>
  );
}
