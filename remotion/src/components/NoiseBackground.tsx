/**
 * AutoMotion — Noise Background Component
 * Animated procedural background using @remotion/noise
 */
import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { noise2D } from "@remotion/noise";
import { useTheme } from "../themes/ThemeProvider";

export const NoiseBackground: React.FC<{
  variant?: "gradient" | "noise" | "grid" | "dots" | "radial" | "solid";
}> = ({ variant = "gradient" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const theme = useTheme();
  const time = frame / fps;

  if (variant === "solid") {
    return (
      <AbsoluteFill style={{ background: theme.colors.bgPrimary }} />
    );
  }

  if (variant === "radial") {
    return (
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at ${50 + Math.sin(time * 0.5) * 10}% ${50 + Math.cos(time * 0.3) * 10}%, ${theme.colors.bgSecondary} 0%, ${theme.colors.bgPrimary} 70%)`,
        }}
      />
    );
  }

  if (variant === "grid") {
    const offset = (time * 20) % 40;
    return (
      <AbsoluteFill style={{ background: theme.colors.bgPrimary }}>
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage: `
              linear-gradient(${theme.colors.accent}15 1px, transparent 1px),
              linear-gradient(90deg, ${theme.colors.accent}15 1px, transparent 1px)
            `,
            backgroundSize: "40px 40px",
            backgroundPosition: `${offset}px ${offset}px`,
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `radial-gradient(ellipse at center, transparent 30%, ${theme.colors.bgPrimary} 100%)`,
          }}
        />
      </AbsoluteFill>
    );
  }

  if (variant === "dots") {
    const offset = (time * 15) % 30;
    return (
      <AbsoluteFill style={{ background: theme.colors.bgPrimary }}>
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage: `radial-gradient(${theme.colors.accent}20 1.5px, transparent 1.5px)`,
            backgroundSize: "30px 30px",
            backgroundPosition: `${offset}px ${offset}px`,
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `radial-gradient(ellipse at center, transparent 30%, ${theme.colors.bgPrimary} 100%)`,
          }}
        />
      </AbsoluteFill>
    );
  }

  // Default: noise/gradient
  // Generate subtle animated noise-based gradient
  const n1 = noise2D("bg1", time * 0.3, 0) * 0.5 + 0.5;
  const n2 = noise2D("bg2", 0, time * 0.2) * 0.5 + 0.5;
  const angle = 135 + n1 * 30;

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(${angle}deg, ${theme.colors.bgPrimary} ${n2 * 20}%, ${theme.colors.bgSecondary} 100%)`,
      }}
    >
      {/* Vignette overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.4) 100%)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};
