// Talks to the rule-engine-service (FastAPI). Search/chat live in core-api-service.
const BASE = (import.meta.env.VITE_RULE_ENGINE_URL ?? "http://localhost:8001").replace(/\/$/, "");

async function request(path, options) {
  let res;
  try {
    res = await fetch(`${BASE}${path}`, options);
  } catch {
    throw new Error(`Can't reach the rule engine at ${BASE}. Is it running?`);
  }
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") message = body.detail;
      else if (Array.isArray(body.detail)) message = body.detail.map((d) => d.msg).join("; ");
    } catch {
      /* body wasn't JSON, keep the generic message */
    }
    throw new Error(message);
  }
  return res;
}

// [{ id, name, jurisdiction, rule_count, rules: [{ id, description, impact }] }]
export async function fetchRegulators() {
  const res = await request("/api/regulators");
  return (await res.json()).regulators;
}

// Uploads the trades CSV and returns the full report (summary, rules_checked, results).
export async function checkTrades(file, regulatorIds) {
  const form = new FormData();
  form.append("file", file);
  regulatorIds.forEach((id) => form.append("regulators", id));
  const res = await request("/api/impact/check", { method: "POST", body: form });
  return res.json();
}

// Sends the report back and saves the CSV the server builds from it.
export async function exportReportCsv(report, filename = "impact-matrix.csv") {
  const res = await request("/api/impact/export", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(report),
  });
  const url = URL.createObjectURL(await res.blob());
  const a = Object.assign(document.createElement("a"), { href: url, download: filename });
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}