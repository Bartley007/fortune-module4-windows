import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "知命 · 个人知识库",
    template: "%s · 知命",
  },
  description: "Module 4 personal knowledge base for the fortune-telling project.",
};

const navigation = [
  { href: "#collections", label: "藏书" },
  { href: "#notes", label: "笔记" },
  { href: "#tags", label: "标签" },
  { href: "#privacy", label: "隐私" },
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>
        <header className="site-header">
          <div className="nav-shell">
            <Link className="brand" href="/">
              <span className="brand-seal">知</span>
              <span>
                <b>知命</b>
                <small>FORTUNE MASTER</small>
              </span>
            </Link>
            <nav aria-label="主导航">
              {navigation.map((item) => (
                <a href={item.href} key={item.href}>
                  {item.label}
                </a>
              ))}
            </nav>
            <Link className="library-link" href="/">
              我的藏书 <span>M4</span>
            </Link>
          </div>
        </header>
        {children}
        <footer className="site-footer">
          <div className="page-shell">
            <div className="brand footer-brand">
              <span className="brand-seal">知</span>
              <span>
                <b>知命</b>
                <small>FORTUNE MASTER</small>
              </span>
            </div>
            <p>规则为骨，典籍为据，语言为桥。</p>
            <p>个人内容仅对当前身份可见。</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
