import Link from "next/link";
import type { DirEntry } from "@/lib/content";
import { subjectLabel } from "@/lib/content";

export function EntryList({ entries, isTopLevel = false }: { entries: DirEntry[]; isTopLevel?: boolean }) {
  if (entries.length === 0) {
    return <p className="text-neutral-500 text-sm">这个目录还没有内容。用 <code>/learn</code> 沉淀。</p>;
  }

  return (
    <ul className="grid gap-2 sm:grid-cols-2">
      {entries.map((e) => {
        const href = `/kb/${e.slug.join("/")}`;
        const isDir = e.type === "dir";
        const displayName = isTopLevel ? subjectLabel(e.name) : e.name;
        const fm = e.type === "file" ? e.frontmatter : e.indexFrontmatter;

        return (
          <li key={href}>
            <Link
              href={href as never}
              className="block rounded border border-neutral-200 dark:border-neutral-800 p-3 hover:border-blue-400 hover:bg-blue-50/40 dark:hover:bg-blue-950/40 transition"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium">
                  <span className="opacity-50 mr-1">{isDir ? "📁" : "📄"}</span>
                  {displayName}
                </span>
                {fm?.new_in_2024_2025 && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
                    新法
                  </span>
                )}
              </div>
              {fm?.id && (
                <div className="text-xs font-mono text-neutral-500">{String(fm.id)}</div>
              )}
              {fm?.aliases && Array.isArray(fm.aliases) && fm.aliases.length > 0 && (
                <div className="text-xs text-neutral-500 mt-1">
                  别名：{fm.aliases.join(" / ")}
                </div>
              )}
            </Link>
          </li>
        );
      })}
    </ul>
  );
}
