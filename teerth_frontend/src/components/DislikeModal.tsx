'use client';

import { useState } from 'react';
import { createPortal } from 'react-dom';
import { DISLIKE_REASONS } from '@/lib/services/article-interaction-service';

interface DislikeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (reason: string, otherReason?: string) => void;
  currentReason?: string;
  currentOtherReason?: string;
}

export default function DislikeModal({
  isOpen,
  onClose,
  onConfirm,
  currentReason,
  currentOtherReason,
}: DislikeModalProps) {
  const [selectedReason, setSelectedReason] = useState<string>(currentReason || '');
  const [otherReason, setOtherReason] = useState<string>(currentOtherReason || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedReason) {
      onConfirm(
        selectedReason,
        selectedReason === 'other' ? otherReason : undefined
      );
      // Reset form
      setSelectedReason('');
      setOtherReason('');
    }
  };

  const handleCancel = () => {
    setSelectedReason('');
    setOtherReason('');
    onClose();
  };

  if (!isOpen) return null;

  const modalContent = (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 pointer-events-auto overflow-y-auto">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm cursor-pointer"
        onClick={handleCancel}
        aria-label="Close modal"
      />

      {/* Modal Container - Wrapper for proper mobile centering */}
      <div className="flex items-center justify-center min-h-full w-full py-4 relative z-10">
        {/* Modal */}
        <div 
          className="relative bg-white dark:bg-amber-100 rounded-2xl shadow-2xl border border-amber-200/50 dark:border-amber-300/50 p-6 md:p-8 max-w-md w-full pointer-events-auto"
          onClick={(e) => e.stopPropagation()}
        >
        {/* Close Button */}
        <button
          onClick={handleCancel}
          className="absolute top-4 right-4 p-2 rounded-full hover:bg-amber-50 dark:hover:bg-amber-200/50 transition-colors"
          aria-label="Close"
        >
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
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
        <h2 className="text-2xl font-bold text-amber-900 dark:text-amber-900 mb-4">
          Why don&apos;t you like this article?
        </h2>
        <p className="text-sm text-amber-700 dark:text-amber-800 mb-6">
          Your feedback helps us improve the content we show you.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="space-y-3 mb-6">
            {DISLIKE_REASONS.map((reason) => (
              <label
                key={reason.value}
                className="flex items-start gap-3 p-3 rounded-lg border border-amber-200 dark:border-amber-300 cursor-pointer hover:bg-amber-50 dark:hover:bg-amber-200/50 transition-colors"
              >
                <input
                  type="radio"
                  name="dislike-reason"
                  value={reason.value}
                  checked={selectedReason === reason.value}
                  onChange={(e) => setSelectedReason(e.target.value)}
                  className="mt-1 w-4 h-4 text-amber-600 border-amber-300 focus:ring-amber-500 focus:ring-2"
                />
                <span className="text-amber-900 dark:text-amber-900 font-medium">
                  {reason.label}
                </span>
              </label>
            ))}
          </div>

          {selectedReason === 'other' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-amber-900 dark:text-amber-900 mb-2">
                Please specify:
              </label>
              <textarea
                value={otherReason}
                onChange={(e) => setOtherReason(e.target.value)}
                placeholder="Tell us more..."
                className="w-full px-4 py-2 border border-amber-300 dark:border-amber-400 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-amber-500 text-amber-900 dark:text-amber-900 bg-white dark:bg-amber-50"
                rows={3}
              />
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleCancel}
              className="flex-1 px-4 py-2 border border-amber-300 dark:border-amber-400 text-amber-700 dark:text-amber-800 rounded-lg hover:bg-amber-50 dark:hover:bg-amber-200/50 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={!selectedReason || (selectedReason === 'other' && !otherReason.trim())}
              className="flex-1 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              Submit
            </button>
          </div>
        </form>
        </div>
      </div>
    </div>
  );

  // Render modal at document body level using portal
  if (typeof window !== 'undefined') {
    return createPortal(modalContent, document.body);
  }

  return null;
}

