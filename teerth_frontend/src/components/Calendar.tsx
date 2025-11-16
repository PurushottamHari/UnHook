'use client';

import { useState } from 'react';

interface CalendarProps {
  selectedDate: string; // YYYY-MM-DD format
  onDateChange: (date: string) => void;
  maxDate?: string; // YYYY-MM-DD format
}

export default function Calendar({
  selectedDate,
  onDateChange,
  maxDate,
}: CalendarProps) {
  const [currentMonth, setCurrentMonth] = useState(() => {
    const date = new Date(selectedDate);
    return new Date(date.getFullYear(), date.getMonth(), 1);
  });

  const today = new Date();
  const todayStr = today.toISOString().split('T')[0];
  const maxDateStr = maxDate || todayStr;

  const selectedDateObj = new Date(selectedDate);

  // Get first day of month and number of days
  const firstDayOfMonth = currentMonth.getDay();
  const daysInMonth = new Date(
    currentMonth.getFullYear(),
    currentMonth.getMonth() + 1,
    0
  ).getDate();

  // Navigate months
  const goToPreviousMonth = () => {
    setCurrentMonth(
      new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1)
    );
  };

  const goToNextMonth = () => {
    const nextMonth = new Date(
      currentMonth.getFullYear(),
      currentMonth.getMonth() + 1,
      1
    );
    const maxDateObj = new Date(maxDateStr);
    // Only allow going to next month if it's not beyond max date
    if (
      nextMonth.getFullYear() < maxDateObj.getFullYear() ||
      (nextMonth.getFullYear() === maxDateObj.getFullYear() &&
        nextMonth.getMonth() <= maxDateObj.getMonth())
    ) {
      setCurrentMonth(nextMonth);
    }
  };

  // Format month/year for display
  const monthYear = currentMonth.toLocaleDateString('en-US', {
    month: 'long',
    year: 'numeric',
  });

  // Handle date selection
  const handleDateClick = (day: number) => {
    const dateStr = `${currentMonth.getFullYear()}-${String(
      currentMonth.getMonth() + 1
    ).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    
    // Don't allow selecting future dates
    if (dateStr <= maxDateStr) {
      onDateChange(dateStr);
    }
  };

  // Check if date is disabled (future date)
  const isDateDisabled = (day: number): boolean => {
    const dateStr = `${currentMonth.getFullYear()}-${String(
      currentMonth.getMonth() + 1
    ).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return dateStr > maxDateStr;
  };

  // Check if date is today
  const isToday = (day: number): boolean => {
    const dateStr = `${currentMonth.getFullYear()}-${String(
      currentMonth.getMonth() + 1
    ).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return dateStr === todayStr;
  };

  // Check if date is selected
  const isSelected = (day: number): boolean => {
    return (
      currentMonth.getFullYear() === selectedDateObj.getFullYear() &&
      currentMonth.getMonth() === selectedDateObj.getMonth() &&
      day === selectedDateObj.getDate()
    );
  };

  // Generate calendar days
  const calendarDays: (number | null)[] = [];
  
  // Add empty cells for days before the first day of the month
  for (let i = 0; i < firstDayOfMonth; i++) {
    calendarDays.push(null);
  }
  
  // Add days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    calendarDays.push(day);
  }

  // Weekday labels
  const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="bg-white dark:bg-amber-100 rounded-xl shadow-lg border border-amber-200 dark:border-amber-300 p-4 w-full max-w-sm">
      {/* Month/Year Header */}
      <div className="flex items-center justify-between mb-4 gap-2">
        <button
          type="button"
          onClick={goToPreviousMonth}
          className="flex-shrink-0 p-2 rounded-md text-amber-600 dark:text-amber-700 hover:bg-amber-50 dark:hover:bg-amber-200 transition-colors focus:outline-none focus:ring-2 focus:ring-amber-500"
          aria-label="Previous month"
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
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>
        
        <h3 className="text-base font-light text-amber-900 dark:text-amber-900 whitespace-nowrap flex-1 text-center">
          {monthYear}
        </h3>
        
        <button
          type="button"
          onClick={goToNextMonth}
          disabled={
            new Date(
              currentMonth.getFullYear(),
              currentMonth.getMonth() + 1,
              1
            ) > new Date(maxDateStr)
          }
          className="flex-shrink-0 p-2 rounded-md text-amber-600 dark:text-amber-700 hover:bg-amber-50 dark:hover:bg-amber-200 transition-colors focus:outline-none focus:ring-2 focus:ring-amber-500 disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Next month"
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
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>
      </div>

      {/* Weekday Labels */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {weekdays.map((day) => (
          <div
            key={day}
            className="text-center text-xs font-medium text-amber-600 dark:text-amber-700 py-1"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 gap-1">
        {calendarDays.map((day, index) => {
          if (day === null) {
            return <div key={index} className="aspect-square" />;
          }

          const disabled = isDateDisabled(day);
          const isTodayDate = isToday(day);
          const isSelectedDate = isSelected(day);

          return (
            <button
              key={index}
              type="button"
              onClick={() => handleDateClick(day)}
              disabled={disabled}
              className={`
                aspect-square rounded-md text-sm font-light transition-all
                focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-1
                ${
                  isSelectedDate
                    ? 'bg-amber-600 dark:bg-amber-700 text-white font-medium'
                    : isTodayDate
                    ? 'bg-amber-100 dark:bg-amber-200 text-amber-900 dark:text-amber-900 font-medium'
                    : disabled
                    ? 'text-amber-300 dark:text-amber-400 cursor-not-allowed'
                    : 'text-amber-700 dark:text-amber-800 hover:bg-amber-50 dark:hover:bg-amber-200'
                }
              `}
              aria-label={`Select ${day}`}
              aria-disabled={disabled}
            >
              {day}
            </button>
          );
        })}
      </div>
    </div>
  );
}

