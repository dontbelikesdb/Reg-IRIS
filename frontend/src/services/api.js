import { searchResults, assistantPrompts } from "../data/mockData.js";

// Swap these mock calls for real backend requests when ready.
const delay = (ms = 300) => new Promise((r) => setTimeout(r, ms));

export async function searchDocuments(query) {
  await delay();
  const q = query.trim().toLowerCase();
  if (!q) return searchResults;
  const words = q.split(/\s+/);
  return searchResults.filter((r) =>
    words.some((w) => `${r.title} ${r.regulator} ${r.snippet}`.toLowerCase().includes(w))
  );
}

export async function askAssistant(question) {
  await delay(500);
  return `Here is a summary related to "${question}". Connect this to your backend to return grounded answers with citations.`;
}

export const suggestedPrompts = assistantPrompts;
