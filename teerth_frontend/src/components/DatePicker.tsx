'use client';

import { useState, useRef, useEffect } from 'react';
import Calendar from './Calendar';

interface DatePickerProps {
  selectedDate: string; // YYYY-MM-DD format
  onDateChange: (date: string) => void;
  className?: string;
}

export default function DatePicker({
  selectedDate,
  onDateChange,
  className = '',
}: DatePickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Format date for display
  const formattedDate = new Date(selectedDate).toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  // Get today's date in YYYY-MM-DD format
  const today = new Date().toISOString().split('T')[0];

  // Close calendar when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [isOpen]);

  // Handle date selection from calendar
  const handleDateChange = (date: string) => {
    onDateChange(date);
    setIsOpen(false);
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {/* Date Display Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="text-sm font-light text-amber-600 dark:text-amber-700 hover:text-amber-800 dark:hover:text-amber-900 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 rounded-md px-2 py-1"
        aria-label="Select date"
        aria-expanded={isOpen}
      >
        <div className="flex items-center gap-2">
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <span>{formattedDate}</span>
        </div>
      </button>

      {/* Custom Calendar Dropdown */}
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 z-50 md:right-0 md:left-auto left-1/2 md:left-auto -translate-x-1/2 md:translate-x-0">
          <Calendar
            selectedDate={selectedDate}
            onDateChange={handleDateChange}
            maxDate={today}
          />
        </div>
      )}
    </div>
  );
}

