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
  const dateObj = new Date(selectedDate);
  const formattedDate = dateObj.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  const shortDate = dateObj.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
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
        className="text-[10px] md:text-sm font-light text-amber-600 dark:text-amber-700 hover:text-amber-800 dark:hover:text-amber-900 transition-colors cursor-pointer focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 rounded-md p-0 md:px-2 md:py-1 leading-none"
        aria-label="Select date"
        aria-expanded={isOpen}
      >
        <div className="flex flex-col md:flex-row items-center justify-center gap-0 md:gap-2">
          <svg
            className="w-3 h-3 md:w-4 md:h-4"
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
          <span className="md:hidden">{shortDate}</span>
          <span className="hidden md:inline">{formattedDate}</span>
        </div>
      </button>

      {/* Mobile Dropdown Modal */}
      {isOpen && (
        <div className="md:hidden">
          <div 
            className="fixed inset-0 z-40 bg-black/20 dark:bg-black/50 backdrop-blur-sm"
            aria-hidden="true"
            onClick={(e) => {
              e.stopPropagation();
              setIsOpen(false);
            }}
          />
          <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50">
            <Calendar
              selectedDate={selectedDate}
              onDateChange={handleDateChange}
              maxDate={today}
            />
          </div>
        </div>
      )}

      {/* Desktop Dropdown */}
      {isOpen && (
        <div className="hidden md:block absolute top-full mt-2 z-50 right-0">
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

