import { ChevronRight } from "lucide-react";

export default function WhatsNewCard({ item, onOpen, compact = false }) {
  return (
    <button className="update-row" onClick={() => onOpen?.(item)}>
      <span className={`status-dot ${item.level}`} />
      <div className="update-main">
        <div className="update-head">
          <span className="tag">{item.regulator}</span>
          <strong>{item.title}</strong>
          {item.isNew && <span className="pill green">New</span>}
        </div>
        <small>{item.date}</small>
        {!compact && <p>{item.summary}</p>}
      </div>
      <ChevronRight size={16} className="chev" />
    </button>
  );
}
