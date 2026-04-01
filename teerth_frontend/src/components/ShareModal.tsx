"use client";

import { useState, useEffect } from "react";
import { toPng } from "html-to-image";
import {
  copyToClipboard,
  isWebShareAvailable,
  shareViaWebAPI,
  type ShareData,
} from "@/lib/share";
import { Article } from "@/models/article.model";
import ArticleShareCard from "@/components/article/ArticleShareCard";

interface ShareModalProps {
  isOpen: boolean;
  onClose: () => void;
  shareData: ShareData;
  article: Article;
}

export default function ShareModal({
  isOpen,
  onClose,
  shareData,
  article,
}: ShareModalProps) {
  const [copied, setCopied] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      // Prevent body scroll when modal is open
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }

    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  // Close modal on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };

    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleCopyLink = async () => {
    const success = await copyToClipboard(shareData.url);
    if (success) {
      setCopied(true);
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    }
  };

  const handleDownload = async () => {
    const element = document.getElementById("article-share-card-export");
    if (!element) return;

    setIsDownloading(true);
    try {
      // Wait a bit for any images to load if needed
      await new Promise((resolve) => setTimeout(resolve, 100));

      const dataUrl = await toPng(element, {
        cacheBust: true,
        width: 1080,
        height: 1920,
        style: {
          opacity: "1",
          visibility: "visible",
        }
      });
      const link = document.createElement("a");

      // Sanitize title for filename
      const sanitizedTitle = article.title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "_")
        .substring(0, 50)
        .replace(/^_|_$/g, "");

      link.href = dataUrl;
      link.download = `${sanitizedTitle}.png`;
      link.click();
    } catch (error) {
      console.error("Error generating image:", error);
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-md z-[60] transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Container */}
      <div className="fixed inset-0 z-[70] flex items-center justify-center p-6 sm:p-10 overflow-y-auto">
        <div
          className="bg-white/95 dark:bg-amber-50/95 backdrop-blur-3xl rounded-[2.5rem] shadow-[0_32px_64px_-12px_rgba(0,0,0,0.15)] max-w-lg md:max-w-4xl w-full transform transition-all my-8 sm:my-12 border border-white dark:border-amber-200/50"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header / Close Button Section */}
          <div className="flex items-center justify-between md:justify-end px-4 sm:px-6 py-2 border-b md:border-none border-amber-200 dark:border-amber-300">
            <div className="w-9 md:hidden" /> {/* Spacer */}
            <h2 className="md:hidden text-lg font-bold text-amber-900">Share Article</h2>
            <button
              onClick={onClose}
              className="p-2 w-9 h-9 flex items-center justify-center rounded-full hover:bg-amber-100 transition-colors"
              aria-label="Close"
            >
              <svg
                className="w-5 h-5 text-amber-800"
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

          {/* Content */}
          <div className="flex flex-col md:flex-row p-4 sm:p-6 md:p-8 gap-6 md:gap-10 items-center justify-center">
            {/* Preview Section */}
            <div className="flex justify-center flex-shrink-0">
              <div className="w-[240px] h-[426px] sm:w-[320px] sm:h-[570px] md:w-[360px] md:h-[640px] shadow-[0_48px_96px_-12px_rgba(0,0,0,0.25)] rounded-3xl overflow-hidden relative bg-[#fffbeb] transition-all duration-300">
                <ArticleShareCard
                  article={article}
                  className="absolute top-0 left-0 pointer-events-none"
                  scale={
                    // Calculate scale based on container width (w/1080)
                    typeof window !== 'undefined' ? (
                      window.innerWidth < 640 ? 0.222222 : // 240/1080
                      window.innerWidth < 768 ? 0.296296 : // 320/1080
                      0.333333 // 360/1080
                    ) : 0.333333
                  }
                />
              </div>
            </div>

            {/* Actions Section */}
            <div className="flex flex-col justify-center w-full md:w-80 gap-4">
              <div className="hidden md:block text-amber-900 text-center mb-2">
                <h3 className="font-bold text-2xl mb-2">Share this article</h3>
                <p className="text-sm opacity-80 px-4">
                  Download a preview card for this article or share the link
                  with others
                </p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-1 gap-3 sm:gap-4">
                {/* Download Action */}
                <button
                  onClick={handleDownload}
                  disabled={isDownloading}
                  className="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-3 px-2 py-3 sm:px-6 sm:py-4 bg-amber-900 hover:bg-black text-white rounded-2xl font-bold transition-all duration-200 shadow-lg disabled:opacity-50 text-sm sm:text-base text-center"
                >
                  {isDownloading ? (
                    <div className="w-5 h-5 flex-shrink-0 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <svg
                      className="w-5 h-5 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2.5}
                        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                      />
                    </svg>
                  )}
                  <span>{isDownloading ? "Generating..." : "Download"}</span>
                </button>

                {/* Copy Link Action */}
                <button
                  onClick={handleCopyLink}
                  className={`flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-3 px-2 py-3 sm:px-6 sm:py-4 rounded-2xl font-bold transition-colors duration-300 shadow-lg border-2 text-sm sm:text-base text-center ${
                    copied
                      ? ""
                      : "bg-white dark:bg-amber-100 border-amber-900 text-amber-900 hover:bg-amber-50 dark:hover:bg-amber-200"
                  }`}
                  style={
                    copied
                      ? {
                          backgroundColor: "#dcfce7", // green-100 equivalent
                          borderColor: "#16a34a", // green-600 equivalent
                          color: "#166534", // green-800 equivalent
                        }
                      : {}
                  }
                >
                  {copied ? (
                    <svg
                      className="w-5 h-5 flex-shrink-0 transition-transform duration-300 scale-110"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2.5}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  ) : (
                    <svg
                      className="w-5 h-5 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2.5}
                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                      />
                    </svg>
                  )}
                  <span>{copied ? "Copied!" : "Copy Link"}</span>
                </button>
              </div>

              {/* Native Share Fallback (Optional) */}
              {isWebShareAvailable() && (
                <div className="text-center pt-2">
                  <button
                    onClick={() => shareViaWebAPI(shareData)}
                    className="text-amber-700 text-sm font-semibold hover:underline"
                  >
                    Other share options...
                  </button>
                </div>
              )}

            </div>
          </div>
        </div>
      </div>

      {/* Hidden container exclusively for perfect 1:1 export capture avoiding CSS transform interference */}
      <div
        className="fixed top-0 left-0 -z-[100] pointer-events-none"
        style={{ width: "1080px", height: "1920px", overflow: "hidden" }}
      >
        <ArticleShareCard id="article-share-card-export" article={article} />
      </div>
    </>
  );
}
