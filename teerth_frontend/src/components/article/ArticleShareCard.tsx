"use client";

import React from "react";
import TeerthLogoIcon from "@/components/TeerthLogoIcon";
import YoutubeBadge from "@/components/YoutubeBadge";
import SourceBadge from "@/components/SourceBadge";
import ReadTimeBadge from "@/components/ReadTimeBadge";
import { Article } from "@/models/article.model";

interface ArticleShareCardProps {
  article: Article;
  /** Optional ID for html2canvas target */
  id?: string;
  /** Scale factor for preview rendering */
  scale?: number;
  className?: string;
}

/**
 * A beautiful, story-sized (9:16) card representing an article.
 * Designed for sharing on Instagram and WhatsApp Stories.
 * Always renders at 1080x1920 px to ensure WYSIWYG consistency.
 * Scale using CSS transforms for previews.
 */
export default function ArticleShareCard({
  article,
  id,
  scale = 1,
  className = "",
}: ArticleShareCardProps) {
  const cleanContent = article.summary
    ? article.summary
    : article.content?.replace(/[#*`]/g, "") || "";

  return (
    <div
      id={id}
      className={`relative flex flex-col font-sans w-[1080px] h-[1920px] p-12 rounded-[60px] overflow-hidden ${className}`}
      style={{
        backgroundColor: "#fffbeb",
        transform: `scale(${scale})`,
        transformOrigin: "top left",
      }}
    >
      <div className="w-full flex items-center justify-center pt-16 pb-10 flex-shrink-0">
        <h1
          className="font-bold text-center w-full text-[70px] leading-[1.1]"
          style={{
            color: "#78350f",
            fontFamily: "serif",
            display: "-webkit-box",
            WebkitLineClamp: 4,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }}
        >
          {article.title}
        </h1>
      </div>

      <div
        className="w-full flex justify-center items-center flex-wrap flex-shrink-0 pt-0 pb-4 gap-10 text-[35px] leading-[40px]"
        style={{ color: "#b45309" }} // amber-700
      >
        {article.youtube_channel ? (
          <YoutubeBadge
            channelName={article.youtube_channel}
            className="flex items-center gap-3"
            iconClassName="flex-shrink-0"
            iconSize={40}
          />
        ) : (
          <SourceBadge
            sourceName={article.article_source || article.category || "Teerth"}
            className="flex items-center gap-3"
            iconClassName="flex-shrink-0"
            iconSize={34}
          />
        )}

        <ReadTimeBadge
          timeToRead={article.time_to_read}
          className="flex items-center justify-center gap-3"
          iconClassName="flex-shrink-0"
          iconSize={40}
        />
      </div>

      {/* 3) Summary Section */}
      <div className="flex-1 w-full flex flex-col justify-start items-center px-8 pt-4 pb-2 overflow-hidden">
        <div
          className="text-center italic w-full text-[42px] leading-[1.5]"
          style={{
            display: "-webkit-box",
            WebkitLineClamp: 17, // Reduced limit to ensure it fits without clipping
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
            color: "#92400e",
            fontWeight: 400,
          }}
        >
          {cleanContent}
        </div>
      </div>

      {/* 4) Footer Section - Logo */}
      <div className="flex flex-col items-center justify-center w-full h-[10.5%] pb-8 flex-shrink-0">
        <TeerthLogoIcon size={180} />
      </div>
    </div>
  );
}
