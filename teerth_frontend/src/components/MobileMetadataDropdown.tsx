'use client';

import { useState, useRef, useEffect, ReactNode } from 'react';

interface MobileMetadataDropdownProps {
  /** The label text for the clickable button (e.g., "In Focus Today:", "Article Info") */
  label: string;
  /** List of React elements to display in the dropdown */
  items: ReactNode[];
}

/**
 * Reusable mobile metadata dropdown component.
 * Shows a clickable button on mobile with a dropdown menu containing the provided items.
 * The dropdown has a transparent backdrop that darkens when opened.
 * 
 * @example
 * ```tsx
 * <MobileMetadataDropdown 
 *   label="Article Info"
 *   items={[
 *     <CategoryTag key="cat" category="Technology" variant="article" />,
 *     <span key="date">January 15, 2024</span>
 *   ]}
 * />
 * ```
 */
export default function MobileMetadataDropdown({
  label,
  items,
}: MobileMetadataDropdownProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      // Use a slight delay to avoid immediate closure
      setTimeout(() => {
        document.addEventListener('mousedown', handleClickOutside);
      }, 0);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropdownOpen]);

  return (
    <div ref={containerRef} className="relative md:hidden mb-3">
      {/* Mobile: Clickable button */}
      <button
        onClick={() => setIsDropdownOpen(!isDropdownOpen)}
        className="flex items-center justify-center gap-2 text-sm font-normal leading-relaxed text-amber-600 dark:text-amber-700 bg-white/70 dark:bg-amber-100/70 backdrop-blur-sm border border-amber-200/30 dark:border-amber-300/30 rounded-lg px-4 py-2.5 hover:bg-white/85 dark:hover:bg-amber-100/85 hover:border-amber-200/40 dark:hover:border-amber-300/40 active:scale-[0.98] transition-all duration-200 inline-flex max-w-xs mx-auto"
      >
        <span>{label}</span>
        <svg
          className={`w-4 h-4 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          strokeWidth={2.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {/* Mobile: Dropdown */}
      {isDropdownOpen && (
        <>
          {/* Backdrop to close on click */}
          <div
            className="fixed inset-0 z-[5] bg-black/10 backdrop-blur-[1px]"
            onClick={() => setIsDropdownOpen(false)}
          />
          {/* Dropdown */}
          <div
            className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 bg-white dark:bg-amber-100 rounded-lg border border-amber-200/20 dark:border-amber-300/20 p-4 z-10 max-h-64 overflow-y-auto scrollbar-hide min-w-[200px] max-w-[90vw] transition-all duration-200 ease-out"
          >
            <div className="text-amber-700 dark:text-amber-800 flex flex-wrap gap-2 justify-center items-center">
              {items.map((item, index) => (
                <div key={index}>{item}</div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

