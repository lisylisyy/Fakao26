import { notFound } from "next/navigation";
import { Breadcrumbs } from "@/components/Breadcrumbs";
import { EntryList } from "@/components/EntryList";
import { FrontmatterChips } from "@/components/Frontmatter";
import { MarkdownView } from "@/components/MarkdownView";
import { isDirectory, listEntries, resolveSlug } from "@/lib/content";

type Params = { slug: string[] };

export default async function KbDocPage({ params }: { params: Promise<Params> }) {
  const { slug: rawSlug } = await params;
  const slug = rawSlug.map((seg) => {
    try {
      return decodeURIComponent(seg);
    } catch {
      return seg;
    }
  });
  const doc = resolveSlug(slug);

  if (!doc && !isDirectory(slug)) {
    notFound();
  }

  const showEntries = isDirectory(slug);
  const children = showEntries ? listEntries(slug) : [];

  return (
    <article>
      <Breadcrumbs slug={slug} />

      {doc && (
        <>
          <FrontmatterChips fm={doc.frontmatter} />
          {doc.content.trim().length > 0 ? (
            <MarkdownView source={doc.content} />
          ) : (
            <p className="text-neutral-500 text-sm italic">这个目录没有 00-index.md 介绍。</p>
          )}
        </>
      )}

      {showEntries && children.length > 0 && (
        <section className="mt-10 pt-6 border-t border-neutral-200 dark:border-neutral-800">
          <h2 className="text-lg font-semibold mb-4">本目录下</h2>
          <EntryList entries={children} />
        </section>
      )}
    </article>
  );
}
