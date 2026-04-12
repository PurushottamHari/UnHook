import { ImageResponse } from "next/og";
import { ArticleService } from "@/lib/services/article-service";
import fs from "fs";
import path from "path";

export const runtime = "nodejs";
export const alt = "Teerth Article Preview";
export const size = {
  width: 1200,
  height: 630,
};
export const contentType = "image/png";

function truncate(text: string, max: number) {
  return text.length > max ? text.slice(0, max - 3) + "..." : text;
}

export default async function Image({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const articleService = new ArticleService();
  const article = await articleService.getArticleById(id);

  const logoPath = path.join(
    process.cwd(),
    "public",
    "assets",
    "logo_base64.txt",
  );
  const logoBase64 = fs.readFileSync(logoPath, "utf-8").trim();
  const logoSrc = `data:image/png;base64,${logoBase64}`;

  if (!article) {
    return new ImageResponse(
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#fffbeb",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ fontSize: 32, fontWeight: "bold", color: "#78350f" }}>
          Article Not Found
        </div>
      </div>,
    );
  }

  const title = truncate(article.title, 100);
  const summary = truncate(article.summary, 700);

  return new ImageResponse(
    <div
      style={{
        height: "100%",
        width: "100%",
        display: "flex",
        flexDirection: "column",
        backgroundColor: "#fefce8",
        fontFamily: "sans-serif",
      }}
    >
      {/* Main content area */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          flex: 1,
          padding: "0px 64px 32px 64px",
        }}
      >
        {/* Title */}
        <div
          style={{
            fontSize: 30,
            fontWeight: "bold",
            color: "#78350f",
            lineHeight: 1.25,
            marginBottom: "22px",
            display: "flex",
            textAlign: "center",
            maxWidth: "900px",
          }}
        >
          {title}
        </div>

        {/* Badge row */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "14px",
            marginBottom: "20px",
          }}
        >
          {/* Category pill — matches CategoryTag compact variant */}
          <div
            style={{
              backgroundColor: "#fde68a",
              color: "#92400e",
              padding: "3px 10px",
              borderRadius: "999px",
              fontSize: 12,
              fontWeight: 500,
              display: "flex",
              letterSpacing: "0.05em",
            }}
          >
            {article.category}
          </div>

          {/* Read time — matches ReadTimeBadge component (book icon + text) */}
          <div
            style={{
              fontSize: 13,
              color: "#d97706",
              fontWeight: 400,
              display: "flex",
              alignItems: "center",
              gap: "6px",
              letterSpacing: "0.025em",
            }}
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#d97706"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <div style={{ display: "flex" }}>{article.time_to_read}</div>
          </div>

          {/* Source / YouTube pill */}
          <div
            style={{
              fontSize: 14,
              color: "#b45309",
              fontWeight: 400,
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            {article.youtube_channel ? (
              <div
                style={{ display: "flex", alignItems: "center", gap: "6px" }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="#b45309">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                </svg>
                <div style={{ display: "flex", fontStyle: "italic" }}>
                  {article.youtube_channel}
                </div>
              </div>
            ) : (
              <div
                style={{ display: "flex", alignItems: "center", gap: "6px" }}
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#b45309"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
                <div style={{ display: "flex" }}>
                  {article.article_source || "Teerth"}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Divider */}
        <div
          style={{
            display: "flex",
            height: "2px",
            backgroundColor: "#fde68a",
            width: "200px",
            marginBottom: "22px",
          }}
        />

        {/* Summary */}
        <div
          style={{
            fontSize: 20,
            color: "#92400e",
            lineHeight: 1.65,
            display: "flex",
            textAlign: "center",
            maxWidth: "860px",
          }}
        >
          {summary}
        </div>
      </div>

      {/* Bottom bar — logo */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "14px 64px",
          backgroundColor: "#fef3c7",
          borderTop: "1px solid #fde68a",
        }}
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={logoSrc}
          alt="Teerth"
          width={160}
          height={44}
          style={{ objectFit: "contain" }}
        />
      </div>
    </div>,
    { ...size },
  );
}
