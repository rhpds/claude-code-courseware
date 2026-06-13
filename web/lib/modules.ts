import fs from "node:fs";
import path from "node:path";

// PatternFly 6 label colors — the Red Hat design-system palette.
export type LabelColor =
  | "blue"
  | "teal"
  | "green"
  | "orange"
  | "purple"
  | "red"
  | "grey"
  | "yellow";

export type Difficulty = "Beginner" | "Intermediate" | "Advanced";

export type ModuleMeta = {
  slug: string; // e.g. "01-vertex-setup"
  num: string; // e.g. "01"
  title: string; // H1 with "Module NN — " stripped
  time: string; // e.g. "10 minutes"
  prerequisites: string;
  description: string;
  isNew: boolean;
  section: string;
  category: string; // short topic label, e.g. "MCP"
  categoryColor: LabelColor;
  difficulty: Difficulty; // learner level, distinct from topic
};

export type Section = {
  name: string;
  modules: ModuleMeta[];
};

// Section grouping mirrors the README catalog. Keyed by module number.
const SECTION_BY_NUM: Record<string, string> = {
  "01": "Setup & Foundation",
  "02": "Setup & Foundation",
  "03": "Core MCP Servers",
  "04": "Core MCP Servers",
  "05": "Core MCP Servers",
  "06": "Core MCP Servers",
  "07": "Core MCP Servers",
  "08": "Core MCP Servers",
  "09": "Skills & Customization",
  "10": "Skills & Customization",
  "21": "Skills & Customization",
  "24": "Security",
  "25": "Security",
  "11": "Advanced Patterns",
  "12": "Advanced Patterns",
  "13": "Advanced Patterns",
  "26": "Advanced Patterns",
  "22": "Parallel & Autonomous Workflows",
  "23": "Parallel & Autonomous Workflows",
  "14": "Workflow & Operations",
  "15": "Workflow & Operations",
  "16": "Workflow & Operations",
  "17": "Workflow & Operations",
  "18": "Workflow & Operations",
  "27": "Workflow & Operations",
  "28": "Workflow & Operations",
  "29": "Workflow & Operations",
  "19": "Team-Customizable",
  "20": "Team-Customizable",
};

const SECTION_ORDER = [
  "Setup & Foundation",
  "Core MCP Servers",
  "Skills & Customization",
  "Security",
  "Advanced Patterns",
  "Parallel & Autonomous Workflows",
  "Workflow & Operations",
  "Team-Customizable",
];

// Short category label + color per section. Colors come from the PatternFly 6
// label palette (Red Hat's design system), so they stay on-brand and pass
// contrast requirements without hardcoding hex values.
const CATEGORY_BY_SECTION: Record<string, { label: string; color: LabelColor }> = {
  "Setup & Foundation": { label: "Setup", color: "blue" },
  "Core MCP Servers": { label: "MCP", color: "teal" },
  "Skills & Customization": { label: "Skills", color: "purple" },
  Security: { label: "Security", color: "red" },
  "Advanced Patterns": { label: "Advanced", color: "orange" },
  "Parallel & Autonomous Workflows": { label: "Autonomous", color: "yellow" },
  "Workflow & Operations": { label: "Workflow", color: "green" },
  "Team-Customizable": { label: "Team", color: "grey" },
};

// Learner level per section, distinct from topic. Rendered as an outline label
// so it reads as a separate dimension from the filled category chip.
const DIFFICULTY_BY_SECTION: Record<string, Difficulty> = {
  "Setup & Foundation": "Beginner",
  "Core MCP Servers": "Beginner",
  "Skills & Customization": "Intermediate",
  Security: "Intermediate",
  "Advanced Patterns": "Advanced",
  "Parallel & Autonomous Workflows": "Advanced",
  "Workflow & Operations": "Intermediate",
  "Team-Customizable": "Intermediate",
};

function modulesDir(): string {
  if (process.env.MODULES_DIR) return process.env.MODULES_DIR;
  // Container builds sync modules into ./content/modules; local dev reads the
  // sibling ../modules directory of the repo.
  const bundled = path.resolve(process.cwd(), "content", "modules");
  if (fs.existsSync(bundled)) return bundled;
  return path.resolve(process.cwd(), "..", "modules");
}

function stripTitle(h1: string): { num: string; title: string } {
  // "# Module 01 — Claude Code + Vertex AI Setup"
  const cleaned = h1.replace(/^#\s+/, "").trim();
  // Separator may be an em-dash, en-dash, or one/two hyphens, with flexible spacing.
  const m = cleaned.match(/^Module\s+(\d+)\s*[—–-]{1,2}\s*(.*)$/);
  if (m) return { num: m[1], title: m[2].trim() };
  return { num: "", title: cleaned };
}

function parseModule(file: string, raw: string): ModuleMeta {
  const slug = file.replace(/\.md$/, "");
  const numFromFile = slug.match(/^(\d+)/)?.[1] ?? "";
  const lines = raw.split("\n");

  const h1 = lines.find((l) => l.startsWith("# ")) ?? `# ${slug}`;
  const { num: numFromTitle, title } = stripTitle(h1);
  const num = numFromTitle || numFromFile;

  const isNew = /<!--\s*NEW\s*-->/.test(raw);
  const time =
    raw.match(/^Estimated time:\s*(.+)$/m)?.[1]?.trim().replace(/\.$/, "") ?? "";
  const prerequisites =
    raw.match(/^Prerequisites:\s*(.+)$/m)?.[1]?.trim() ?? "None";

  // Description: first prose paragraph after the metadata header lines.
  let description = "";
  let started = false;
  const buf: string[] = [];
  for (const line of lines) {
    if (line.startsWith("# ")) continue;
    if (/^<!--/.test(line)) continue;
    if (/^(Estimated time:|Prerequisites:)/.test(line)) {
      started = true;
      continue;
    }
    if (!started) continue;
    if (line.startsWith("## ")) break;
    if (line.trim() === "") {
      if (buf.length) break;
      continue;
    }
    buf.push(line.trim());
  }
  description = buf.join(" ");

  const section = SECTION_BY_NUM[num] ?? "Other";
  const cat = CATEGORY_BY_SECTION[section] ?? { label: "Other", color: "grey" as LabelColor };

  return {
    slug,
    num,
    title,
    time,
    prerequisites,
    description,
    isNew,
    section,
    category: cat.label,
    categoryColor: cat.color,
    difficulty: DIFFICULTY_BY_SECTION[section] ?? "Intermediate",
  };
}

export function getAllModules(): ModuleMeta[] {
  const dir = modulesDir();
  const files = fs
    .readdirSync(dir)
    .filter((f) => /^\d+.*\.md$/.test(f) && f !== "TEMPLATE.md");
  const mods = files.map((f) => parseModule(f, fs.readFileSync(path.join(dir, f), "utf8")));
  return mods.sort((a, b) => a.num.localeCompare(b.num));
}

export function getSections(): Section[] {
  const mods = getAllModules();
  const sections: Section[] = SECTION_ORDER.map((name) => ({
    name,
    modules: mods.filter((m) => m.section === name),
  })).filter((s) => s.modules.length > 0);
  const other = mods.filter((m) => !SECTION_ORDER.includes(m.section));
  if (other.length) sections.push({ name: "Other", modules: other });
  return sections;
}

export function getModule(slug: string): { meta: ModuleMeta; body: string } | null {
  const dir = modulesDir();
  const file = path.join(dir, `${slug}.md`);
  if (!fs.existsSync(file)) return null;
  const raw = fs.readFileSync(file, "utf8");
  const meta = parseModule(`${slug}.md`, raw);
  // Strip the H1 and metadata header lines from the body — they're rendered
  // separately in the page header.
  const body = raw
    .replace(/^#\s+Module.*$/m, "")
    .replace(/^<!--\s*NEW\s*-->\s*$/m, "")
    .replace(/^Estimated time:.*$/m, "")
    .replace(/^Prerequisites:.*$/m, "")
    .trimStart();
  return { meta, body };
}
