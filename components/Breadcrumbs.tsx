import Link from "next/link";
import { subjectLabel } from "@/lib/content";

export function Breadcrumbs({ slug }: { slug: string[] }) {
  const crumbs = [
    { label: "知识库", href: "/kb" as const },
    ...slug.map((seg, i) => ({
      label: i === 0 ? subjectLabel(seg) : seg,
      href: `/kb/${slug.slice(0, i + 1).join("/")}` as const,
    })),
  ];

  return (
    <nav className="text-sm text-neutral-500 mb-4 flex flex-wrap gap-1 items-center">
      {crumbs.map((c, i) => (
        <span key={i} className="flex items-center gap-1">
          {i > 0 && <span className="opacity-50">/</span>}
          {i < crumbs.length - 1 ? (
            <Link href={c.href as never} className="hover:underline">
              {c.label}
            </Link>
          ) : (
            <span className="text-neutral-700 dark:text-neutral-300 font-medium">{c.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}
