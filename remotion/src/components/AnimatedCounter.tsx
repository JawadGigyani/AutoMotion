/**
 * RepoReel — Animated Counter Component
 * Counts from 0 to target number over a set duration.
 */
import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import { useTheme } from "../themes/ThemeProvider";

export const AnimatedCounter: React.FC<{
  value: number;
  label: string;
  suffix?: string;
  delay?: number;
  fontSize?: number;
}> = ({ value, label, suffix = "", delay = 0, fontSize = 72 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = useTheme();

  const elapsed = Math.max(0, frame - delay);
  const duration = fps * 1.5;

  const progress = interpolate(elapsed, [0, duration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Ease out cubic
  const eased = 1 - Math.pow(1 - progress, 3);
  const displayValue = Math.floor(eased * value);

  const opacity = interpolate(elapsed, [0, 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const formatNumber = (n: number): string => {
    if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
    return n.toLocaleString();
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        opacity,
        gap: 8,
      }}
    >
      <span
        style={{
          fontSize,
          fontWeight: 800,
          fontFamily: theme.fonts.heading,
          color: theme.colors.accent,
          letterSpacing: "-2px",
        }}
      >
        {formatNumber(displayValue)}{suffix}
      </span>
      <span
        style={{
          fontSize: 22,
          fontWeight: 400,
          fontFamily: theme.fonts.body,
          color: theme.colors.textMuted,
          textTransform: "uppercase",
          letterSpacing: "2px",
        }}
      >
        {label}
      </span>
    </div>
  );
};
