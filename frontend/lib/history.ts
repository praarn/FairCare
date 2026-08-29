export interface HistoryEntry {
  treatment_id: string;
  treatment_name: string;
  city: string;
  hospital_type?: string;
  viewed_at: number;
}

const KEY = "faircare_history";
const MAX_ENTRIES = 15;

export function getHistory(): HistoryEntry[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as HistoryEntry[]) : [];
  } catch {
    return [];
  }
}

export function addHistoryEntry(entry: Omit<HistoryEntry, "viewed_at">) {
  if (typeof window === "undefined") return;
  try {
    const existing = getHistory().filter(
      (e) =>
        !(
          e.treatment_id === entry.treatment_id &&
          e.city === entry.city &&
          e.hospital_type === entry.hospital_type
        )
    );
    const updated = [{ ...entry, viewed_at: Date.now() }, ...existing].slice(0, MAX_ENTRIES);
    window.localStorage.setItem(KEY, JSON.stringify(updated));
  } catch {
    // Storage can fail (private browsing, quota, disabled) — history is a
    // nice-to-have, so we just silently skip rather than breaking the page.
  }
}

export function clearHistory() {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(KEY);
  } catch {
    // ignore
  }
}
