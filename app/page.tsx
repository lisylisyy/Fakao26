import Link from "next/link";
import { listSubjects, subjectLabel } from "@/lib/content";

export default function HomePage() {
  const subjects = listSubjects().filter((s) => s.name !== "_meta");

  return (
    <div>
      <section className="mb-12">
        <h1 className="text-3xl font-bold mb-2">Fakao26 — 法考 2026 备考</h1>
        <p className="text-neutral-600 dark:text-neutral-400">
          通过 2026 年 9 月法考客观题（180/300）的个人备考操作系统。
          知识库 + 题库 + 学习状态，三层架构，git 多设备同步。
        </p>
      </section>

      <section className="mb-10">
        <h2 className="text-xl font-semibold mb-3">学科入口</h2>
        <ul className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          {subjects.map((s) => (
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

      <section>
        <h2 className="text-xl font-semibold mb-3">参考</h2>
        <ul className="text-sm space-y-1 list-disc pl-5 text-neutral-700 dark:text-neutral-300">
          <li>
            <Link href={"/kb/_meta/exam-structure" as never} className="text-blue-600 hover:underline dark:text-blue-400">
              考试结构 + 分值分布
            </Link>
          </li>
          <li>
            <Link href={"/kb/_meta/new-laws-2024-2025" as never} className="text-blue-600 hover:underline dark:text-blue-400">
              2024-2025 新法清单
            </Link>
          </li>
          <li>
            <Link href={"/kb/_meta/frontmatter-spec" as never} className="text-blue-600 hover:underline dark:text-blue-400">
              frontmatter 规范
            </Link>
          </li>
        </ul>
      </section>
    </div>
  );
}
