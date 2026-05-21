import Link from "next/link";
import { listSubjects, subjectLabel } from "@/lib/content";

export default function KbRootPage() {
  const subjects = listSubjects();
  const exam = subjects.filter((s) => s.name !== "_meta");
  const meta = subjects.find((s) => s.name === "_meta");

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">知识库</h1>
      <p className="text-sm text-neutral-500 mb-6">
        所有内容来自 <code>content/</code>。用 <code>/learn</code> 沉淀新知识点。
      </p>

      <section className="mb-10">
        <h2 className="text-lg font-semibold mb-3">8 大学科</h2>
        <ul className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          {exam.map((s) => (
            <li key={s.name}>
              <Link
                href={`/kb/${s.name}` as never}
                className="block rounded border border-neutral-200 dark:border-neutral-800 p-3 hover:border-blue-400 hover:bg-blue-50/40 dark:hover:bg-blue-950/40 transition"
              >
                <div className="font-medium">{subjectLabel(s.name)}</div>
                <div className="text-xs text-neutral-500 font-mono">{s.name}</div>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      {meta && (
        <section>
          <h2 className="text-lg font-semibold mb-3">元数据</h2>
          <Link
            href={`/kb/${meta.name}` as never}
            className="inline-block rounded border border-neutral-200 dark:border-neutral-800 px-3 py-2 hover:border-blue-400 transition text-sm"
          >
            📁 _meta — 大纲跟踪 / 新法清单 / 考试结构 / frontmatter 规范
          </Link>
        </section>
      )}
    </div>
  );
}
