/**
 * RepoReel — Badge/Pill Component
 */
import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { useTheme } from "../themes/ThemeProvider";

export const Badge: React.FC<{
  text: string;
  index?: number;
  style?: React.CSSProperties;
}> = ({ text, index = 0, style }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = useTheme();

  const delay = index * 4;
  const progress = spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        padding: "10px 24px",
        borderRadius: 50,
        backgroundColor: `${theme.colors.accent}22`,
        border: `1px solid ${theme.colors.accent}55`,
        color: theme.colors.accent,
        fontSize: 26,
        fontFamily: theme.fonts.body,
        fontWeight: 500,
        opacity: progress,
        transform: `translateY(${(1 - progress) * 20}px) scale(${0.8 + progress * 0.2})`,
        ...style,
      }}
    >
      {text}
    </div>
  );
};
