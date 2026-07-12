import React, { useState, useMemo } from "react";
import { slugify } from "@/lib/slugify";

interface TableOfContentsProps {
  content: string;
}

interface Heading {
  level: number;
  text: string;
  id: string;
}

export default function ArticleTableOfContents({
  content,
}: TableOfContentsProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleScroll = (e: React.MouseEvent<HTMLAnchorElement>, id: string) => {
    e.preventDefault();
    setIsOpen(false);
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
      // Update URL hash without jumping
      window.history.pushState(null, "", `#${id}`);
    }
  };

  const headings = useMemo(() => {
    // Regex matches Markdown headings like "# Heading", "## Heading", etc.
    const headingRegex = /^(#{1,3})\s+(.+)$/gm;
    const extractedHeadings: Heading[] = [];
    let match;

    while ((match = headingRegex.exec(content)) !== null) {
      const level = match[1].length;
      // Strip any markdown links from the heading text for cleaner display
      const text = match[2].replace(/\[([^\]]+)\]\([^\)]+\)/g, "$1").trim();
      extractedHeadings.push({
        level,
        text,
        id: slugify(text),
      });
    }

    return extractedHeadings;
  }, [content]);

  if (headings.length === 0) return null;

  return (
    <>
      {/* Floating Action Button (Middle Left) */}
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed left-0 top-[20%] -translate-y-1/2 w-8 h-32 sm:h-40 flex items-center justify-start group z-[100] transition-all duration-300 ease-in-out cursor-pointer ${
          isOpen ? "-translate-x-full opacity-0" : "translate-x-0 opacity-50"
        }`}
        aria-label="Table of Contents"
        title="Table of Contents"
      >
        {/* Slidable Dock Pill / Gesture Handle */}
        <div className="w-2 h-16 sm:h-20 bg-amber-500/50 dark:bg-amber-400/50 group-hover:bg-amber-500 dark:group-hover:bg-amber-400 rounded-r-full shadow-sm backdrop-blur-sm transition-all duration-300 ease-out group-hover:w-3 group-hover:h-20 sm:group-hover:h-24" />
      </button>

      {/* Drawer Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/20 dark:bg-black/40 z-40 transition-opacity backdrop-blur-[1px]"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Drawer */}
      <div
        className={`fixed top-0 left-0 h-full w-64 sm:w-72 bg-yellow-50/90 dark:bg-amber-50/90 backdrop-blur-md shadow-2xl z-50 transform transition-transform duration-300 ease-out rounded-r-2xl ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        } overflow-y-auto border-r border-y border-amber-200/50 dark:border-amber-300/50`}
      >
        <div className="p-5 flex items-center justify-between border-b border-amber-200/50 dark:border-amber-300/50 sticky top-0 bg-yellow-50/90 dark:bg-amber-50/90 z-10 backdrop-blur-sm">
          <h2 className="text-lg font-bold text-amber-900 dark:text-amber-900 flex items-center gap-2">
            <svg
              className="w-5 h-5 text-amber-600 dark:text-amber-700"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h7"
              />
            </svg>
            Contents
          </h2>
          <button
            onClick={() => setIsOpen(false)}
            className="text-amber-600 hover:text-amber-900 dark:text-amber-700 dark:hover:text-amber-900 p-1.5 rounded-lg transition-colors"
            aria-label="Close Table of Contents"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
        <nav className="p-5">
          <ul className="space-y-3.5">
            {headings.map((heading, idx) => (
              <li
                key={`${heading.id}-${idx}`}
                style={{ marginLeft: `${(heading.level - 1) * 1.25}rem` }}
              >
                <a
                  href={`#${heading.id}`}
                  onClick={(e) => handleScroll(e, heading.id)}
                  className={`block text-[15px] leading-tight text-amber-800 hover:text-amber-600 dark:text-amber-800 dark:hover:text-amber-900 transition-colors ${
                    heading.level === 1
                      ? "font-semibold text-amber-900 dark:text-amber-900"
                      : ""
                  }`}
                >
                  {heading.text}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </>
  );
}
