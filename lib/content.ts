import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";

const CONTENT_ROOT = path.join(process.cwd(), "content");

export type Frontmatter = {
  id?: string;
  subject?: string;
  concept_ids?: string[];
  parent_concept?: string;
  aliases?: string[];
  weight?: number;
  difficulty?: number;
  new_in_2024_2025?: boolean;
  syllabus_year?: number;
  updated_at?: string;
  status?: string;
  [key: string]: unknown;
};

export type DocFile = {
  slug: string[];
  filePath: string;
  frontmatter: Frontmatter;
  content: string;
};

export type DirEntry =
  | {
      type: "file";
      name: string;        // 01-罪刑法定原则
      slug: string[];      // ["criminal", "01-罪刑法定原则"]
      frontmatter: Frontmatter;
    }
  | {
      type: "dir";
      name: string;        // criminal
      slug: string[];      // ["criminal"]
      hasIndex: boolean;
      indexFrontmatter?: Frontmatter;
    };

function slugToFsPath(slug: string[]): string {
  return path.join(CONTENT_ROOT, ...slug);
}

function fsPathToSlug(fsPath: string): string[] {
  const rel = path.relative(CONTENT_ROOT, fsPath);
  if (!rel) return [];
  return rel.split(path.sep);
}

function isMarkdown(name: string): boolean {
  return name.toLowerCase().endsWith(".md");
}

function stripMdExt(name: string): string {
  return name.replace(/\.md$/i, "");
}

function readMarkdownAt(fsPath: string): { frontmatter: Frontmatter; content: string } | null {
  if (!fs.existsSync(fsPath)) return null;
  const raw = fs.readFileSync(fsPath, "utf-8");
  const { data, content } = matter(raw);
  return { frontmatter: data as Frontmatter, content };
}

/** 列出 content/ 顶层学科目录 */
export function listSubjects(): DirEntry[] {
  if (!fs.existsSync(CONTENT_ROOT)) return [];
  const entries = fs.readdirSync(CONTENT_ROOT, { withFileTypes: true });
  return entries
    .filter((e) => e.isDirectory())
    .map((e): DirEntry => {
      const indexPath = path.join(CONTENT_ROOT, e.name, "00-index.md");
      const idx = readMarkdownAt(indexPath);
      return {
        type: "dir",
        name: e.name,
        slug: [e.name],
        hasIndex: idx !== null,
        indexFrontmatter: idx?.frontmatter,
      };
    })
    .sort((a, b) => a.name.localeCompare(b.name));
}

/** 列出某目录下的子条目（文件 + 子目录），不包含 00-index.md 自身 */
export function listEntries(slug: string[]): DirEntry[] {
  const dirPath = slugToFsPath(slug);
  if (!fs.existsSync(dirPath) || !fs.statSync(dirPath).isDirectory()) return [];

  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  const result: DirEntry[] = [];

  for (const e of entries) {
    if (e.name.startsWith(".")) continue;
    if (e.name === "00-index.md") continue; // 在父页面已渲染
    if (e.isDirectory()) {
      const indexPath = path.join(dirPath, e.name, "00-index.md");
      const idx = readMarkdownAt(indexPath);
      result.push({
        type: "dir",
        name: e.name,
        slug: [...slug, e.name],
        hasIndex: idx !== null,
        indexFrontmatter: idx?.frontmatter,
      });
    } else if (e.isFile() && isMarkdown(e.name)) {
      const filePath = path.join(dirPath, e.name);
      const parsed = readMarkdownAt(filePath);
      if (!parsed) continue;
      result.push({
        type: "file",
        name: stripMdExt(e.name),
        slug: [...slug, stripMdExt(e.name)],
        frontmatter: parsed.frontmatter,
      });
    }
  }

  // 文件按文件名升序（自然带了 01- 02- 顺序），目录排在前面
  result.sort((a, b) => {
    if (a.type !== b.type) return a.type === "dir" ? -1 : 1;
    return a.name.localeCompare(b.name);
  });

  return result;
}

/**
 * 根据 slug 解析为：
 * - 如果对应 <slug>.md → 文件
 * - 如果对应目录 → 取目录下 00-index.md（若有）
 * 返回 null 表示找不到
 */
export function resolveSlug(slug: string[]): DocFile | null {
  if (slug.length === 0) {
    // /kb 根：取 content/00-index.md 如果有；否则返回 null（页面会用 listSubjects 渲染）
    const rootIdx = readMarkdownAt(path.join(CONTENT_ROOT, "00-index.md"));
    if (!rootIdx) return null;
    return { slug: [], filePath: path.join(CONTENT_ROOT, "00-index.md"), ...rootIdx };
  }

  const asFile = slugToFsPath(slug) + ".md";
  if (fs.existsSync(asFile) && fs.statSync(asFile).isFile()) {
    const parsed = readMarkdownAt(asFile);
    if (parsed) return { slug, filePath: asFile, ...parsed };
  }

  const asDir = slugToFsPath(slug);
  if (fs.existsSync(asDir) && fs.statSync(asDir).isDirectory()) {
    const idxPath = path.join(asDir, "00-index.md");
    const parsed = readMarkdownAt(idxPath);
    if (parsed) return { slug, filePath: idxPath, ...parsed };
    // 目录存在但无 index：返回伪文档（页面会只展示子条目）
    return {
      slug,
      filePath: asDir,
      frontmatter: { id: slug.join("."), subject: slug[0] },
      content: "",
    };
  }

  return null;
}

/** 判断给定 slug 路径是否对应一个目录 */
export function isDirectory(slug: string[]): boolean {
  const fsPath = slugToFsPath(slug);
  return fs.existsSync(fsPath) && fs.statSync(fsPath).isDirectory();
}

/** 给 generateStaticParams 用：递归列出所有 markdown 的 slug（不含根） */
export function getAllSlugs(): string[][] {
  const out: string[][] = [];
  function walk(dir: string) {
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      if (e.name.startsWith(".")) continue;
      const full = path.join(dir, e.name);
      if (e.isDirectory()) {
        out.push(fsPathToSlug(full));
        walk(full);
      } else if (e.isFile() && isMarkdown(e.name)) {
        out.push(fsPathToSlug(full).map((p, i, arr) => (i === arr.length - 1 ? stripMdExt(p) : p)));
      }
    }
  }
  if (fs.existsSync(CONTENT_ROOT)) walk(CONTENT_ROOT);
  return out;
}

/** 学科中文名映射（用于 UI 显示） */
export const SUBJECT_LABELS: Record<string, string> = {
  theory: "理论法",
  international: "三国法",
  criminal: "刑法",
  "criminal-procedure": "刑事诉讼法",
  civil: "民法",
  "civil-procedure": "民事诉讼法",
  administrative: "行政法",
  commercial: "商经法",
  _meta: "元数据",
};

export function subjectLabel(name: string): string {
  return SUBJECT_LABELS[name] ?? name;
}
