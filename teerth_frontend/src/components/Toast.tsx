'use client';

import { useEffect, useState } from 'react';

interface ToastProps {
  message: string;
  isVisible: boolean;
  onClose: () => void;
  duration?: number;
}

export default function Toast({
  message,
  isVisible,
  onClose,
  duration = 2000,
}: ToastProps) {
  const [shouldRender, setShouldRender] = useState(isVisible);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    if (isVisible) {
      setShouldRender(true);
      // Slight delay to ensure the DOM updates before adding the animation classes
      timeoutId = setTimeout(() => setIsAnimating(true), 10);
    } else {
      setIsAnimating(false);
    }
    return () => clearTimeout(timeoutId);
  }, [isVisible]);

  useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [isVisible, duration, onClose]);

  if (!shouldRender) return null;

  return (
    <div
      className={`fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 transition-all duration-200 ease-out ${
        isAnimating ? 'opacity-100 scale-100' : 'opacity-0 scale-90'
      }`}
      onTransitionEnd={() => {
        if (!isVisible && !isAnimating) {
          setShouldRender(false);
        }
      }}
    >
      <div className="bg-white dark:bg-amber-50 border border-amber-200 dark:border-amber-300 text-amber-900 dark:text-amber-900 px-8 py-6 rounded-xl shadow-2xl flex items-center justify-center gap-4 min-w-[320px] max-w-[90vw]">
        <svg
          className="w-7 h-7 flex-shrink-0 text-amber-600 dark:text-amber-700"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 13l4 4L19 7"
          />
        </svg>
        <span className="text-base sm:text-lg font-medium">{message}</span>
      </div>
    </div>
  );
}

