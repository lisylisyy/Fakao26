import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Fakao26 — 法考 2026 备考",
  description: "法考 2026 客观题备考系统",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>
        <header className="border-b border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900">
          <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
            <Link href="/" className="font-bold text-lg">
              Fakao26
            </Link>
            <nav className="flex gap-6 text-sm">
              <Link href="/" className="hover:underline">首页</Link>
              <Link href="/kb" className="hover:underline">知识库</Link>
              <span className="text-neutral-400">刷题（W2）</span>
              <span className="text-neutral-400">复习（W3）</span>
              <span className="text-neutral-400">统计（W4）</span>
            </nav>
          </div>
        </header>
        <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>
        <footer className="max-w-6xl mx-auto px-6 py-8 text-xs text-neutral-500 border-t border-neutral-200 dark:border-neutral-800 mt-12">
          法考 2026 客观题备考系统 · 距 9 月考试还有 ~4 个月
        </footer>
      </body>
    </html>
  );
}
