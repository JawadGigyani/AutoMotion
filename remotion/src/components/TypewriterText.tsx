/**
 * RepoReel — Typewriter Text Component
 * Reveals text character-by-character synced to frame count.
 */
import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { useTheme } from "../themes/ThemeProvider";

export const TypewriterText: React.FC<{
  text: string;
  startFrame?: number;
  charsPerSecond?: number;
  fontSize?: number;
  color?: string;
  fontWeight?: number;
}> = ({
  text,
  startFrame = 0,
  charsPerSecond = 30,
  fontSize = 40,
  color,
  fontWeight = 400,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = useTheme();

  const elapsed = Math.max(0, frame - startFrame);
  const framesPerChar = fps / charsPerSecond;
  const charsVisible = Math.min(text.length, Math.floor(elapsed / framesPerChar));

  const displayText = text.slice(0, charsVisible);
  const showCursor = charsVisible < text.length && elapsed % (fps / 2) < fps / 4;

  return (
    <div
      style={{
        fontSize,
        fontWeight,
        fontFamily: theme.fonts.body,
        color: color || theme.colors.text,
        lineHeight: 1.5,
        maxWidth: "85%",
      }}
    >
      {displayText}
      {showCursor && (
        <span
          style={{
            color: theme.colors.accent,
            fontWeight: 100,
          }}
        >
          |
        </span>
      )}
    </div>
  );
};
