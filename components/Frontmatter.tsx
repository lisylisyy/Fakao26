import type { Frontmatter } from "@/lib/content";
import { subjectLabel } from "@/lib/content";

export function FrontmatterChips({ fm }: { fm: Frontmatter }) {
  const items: { label: string; value: string; tone?: "default" | "warn" | "info" }[] = [];

  if (fm.subject) items.push({ label: "学科", value: subjectLabel(fm.subject), tone: "info" });
  if (fm.id) items.push({ label: "id", value: String(fm.id) });
  if (typeof fm.weight === "number") items.push({ label: "命题热度", value: "★".repeat(fm.weight) + "☆".repeat(Math.max(0, 5 - fm.weight)) });
  if (typeof fm.difficulty === "number") items.push({ label: "难度", value: "★".repeat(fm.difficulty) + "☆".repeat(Math.max(0, 5 - fm.difficulty)) });
  if (fm.new_in_2024_2025) items.push({ label: "新法", value: "2024-2025", tone: "warn" });
  if (fm.syllabus_year) items.push({ label: "大纲", value: String(fm.syllabus_year) });
  if (fm.updated_at) items.push({ label: "更新", value: String(fm.updated_at) });
  if (fm.status) items.push({ label: "状态", value: String(fm.status), tone: "warn" });

  if (items.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mb-6 text-xs">
      {items.map((it, i) => (
        <span
          key={i}
          className={
            "inline-flex items-center gap-1 px-2 py-1 rounded border " +
            (it.tone === "warn"
              ? "border-amber-400 bg-amber-50 text-amber-800 dark:bg-amber-950 dark:text-amber-200"
              : it.tone === "info"
                ? "border-blue-400 bg-blue-50 text-blue-800 dark:bg-blue-950 dark:text-blue-200"
                : "border-neutral-300 bg-neutral-50 text-neutral-700 dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-300")
          }
        >
          <span className="opacity-60">{it.label}</span>
          <span className="font-mono">{it.value}</span>
        </span>
      ))}
      {Array.isArray(fm.aliases) && fm.aliases.length > 0 && (
        <span className="inline-flex items-center gap-1 px-2 py-1 rounded border border-neutral-300 bg-neutral-50 text-neutral-700 dark:border-neutral-700 dark:bg-neutral-900 dark:text-neutral-300">
          <span className="opacity-60">别名</span>
          <span>{fm.aliases.join(" / ")}</span>
        </span>
      )}
    </div>
  );
}
