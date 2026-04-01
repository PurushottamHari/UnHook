import React from 'react';

interface SourceBadgeProps {
  sourceName: React.ReactNode;
  className?: string;
  iconClassName?: string;
  iconSize?: number | string;
}

export default function SourceBadge({
  sourceName,
  className = "flex items-center gap-2",
  iconClassName = "w-4 h-4 flex-shrink-0",
  iconSize,
}: SourceBadgeProps) {
  return (
    <div className={className}>
      <svg
        className={iconClassName}
        width={iconSize || "1em"}
        height={iconSize || "1em"}
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"

        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
      </svg>
      <span className="tracking-wide">{sourceName}</span>
    </div>
  );
}
