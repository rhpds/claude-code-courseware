// Client-side progress tracking via localStorage. Offline-friendly and
// requires no backend; progress is per-browser.

const KEY = "courseware-progress";

export type Progress = Record<string, boolean>;

export function loadProgress(): Progress {
  if (typeof window === "undefined") return {};
  try {
    return JSON.parse(window.localStorage.getItem(KEY) || "{}");
  } catch {
    return {};
  }
}

export function setComplete(slug: string, complete: boolean): Progress {
  const current = loadProgress();
  if (complete) current[slug] = true;
  else delete current[slug];
  window.localStorage.setItem(KEY, JSON.stringify(current));
  return current;
}
