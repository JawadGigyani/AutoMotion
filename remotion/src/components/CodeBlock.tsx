/**
 * AutoMotion — Code Block Component
 * VS Code-inspired code display with line-by-line reveal.
 */
import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { useTheme } from "../themes/ThemeProvider";

export const CodeBlock: React.FC<{
  code: string;
  filename?: string;
  caption?: string;
}> = ({ code, filename = "index.ts", caption }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = useTheme();

  const lines = code.split("\n").slice(0, 12);
  const framesPerLine = Math.max(2, Math.floor((fps * 2) / Math.max(lines.length, 1)));

  return (
    <div
      style={{
        width: "85%",
        borderRadius: 16,
        overflow: "hidden",
        boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
        border: `1px solid ${theme.colors.accent}30`,
      }}
    >
      {/* Title bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          padding: "14px 20px",
          backgroundColor: `${theme.colors.codeBg}`,
          borderBottom: `1px solid ${theme.colors.accent}20`,
        }}
      >
        <div style={{ display: "flex", gap: 8 }}>
          <div style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: "#ff5f57" }} />
          <div style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: "#febc2e" }} />
          <div style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: "#28c840" }} />
        </div>
        <span
          style={{
            fontSize: 16,
            color: theme.colors.textMuted,
            fontFamily: theme.fonts.code,
            marginLeft: 8,
          }}
        >
          {filename}
        </span>
      </div>

      {/* Code area */}
      <div
        style={{
          padding: "20px 24px",
          backgroundColor: theme.colors.codeBg,
          fontFamily: theme.fonts.code,
          fontSize: 22,
          lineHeight: 1.7,
        }}
      >
        {lines.map((line, i) => {
          const lineProgress = interpolate(
            frame,
            [i * framesPerLine, i * framesPerLine + 8],
            [0, 1],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
          );

          return (
            <div
              key={i}
              style={{
                display: "flex",
                opacity: lineProgress,
                transform: `translateX(${(1 - lineProgress) * 15}px)`,
              }}
            >
              <span
                style={{
                  width: 45,
                  textAlign: "right",
                  marginRight: 20,
                  color: theme.colors.textMuted,
                  fontSize: 18,
                  userSelect: "none",
                }}
              >
                {i + 1}
              </span>
              <span style={{ color: theme.colors.codeText }}>
                {line || " "}
              </span>
            </div>
          );
        })}
      </div>

      {/* Caption */}
      {caption && (
        <div
          style={{
            padding: "12px 24px",
            backgroundColor: `${theme.colors.accent}15`,
            borderTop: `1px solid ${theme.colors.accent}20`,
            color: theme.colors.textMuted,
            fontSize: 18,
            fontFamily: theme.fonts.body,
          }}
        >
          {caption}
        </div>
      )}
    </div>
  );
};
