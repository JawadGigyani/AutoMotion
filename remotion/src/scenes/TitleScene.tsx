/**
 * AutoMotion — Title Scene
 * Project name with tagline. Layout adapts per theme (centered vs left-aligned).
 */
import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";
import { useTheme } from "../themes/ThemeProvider";
import { NoiseBackground } from "../components/NoiseBackground";

export const TitleScene: React.FC<{
  content: { title?: string; tagline?: string };
  background_variant?: string;
}> = ({ content, background_variant = "gradient" }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const theme = useTheme();
  const { layout } = theme;

  const titleProgress = spring({
    frame,
    fps,
    config: { damping: 14, stiffness: 80 },
  });
  const taglineProgress = spring({
    frame: Math.max(0, frame - 12),
    fps,
    config: { damping: 16, stiffness: 70 },
  });
  const lineWidth = interpolate(titleProgress, [0, 1], [0, 120]);

  const exitStart = Math.max(0, durationInFrames - 10);
  const exitOpacity = interpolate(
    frame,
    [exitStart, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const isLeft = layout.titleAlign === "left";

  return (
    <AbsoluteFill>
      <NoiseBackground variant={background_variant as any} />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: isLeft ? "flex-start" : "center",
          padding: isLeft ? "80px 120px" : 80,
          opacity: exitOpacity,
        }}
      >
        <div
          style={{
            fontSize: layout.titleSize,
            fontWeight: 800,
            fontFamily: theme.fonts.heading,
            color: theme.colors.text,
            textAlign: isLeft ? "left" : "center",
            letterSpacing: "-2px",
            opacity: titleProgress,
            transform: isLeft
              ? `translateX(${(1 - titleProgress) * -60}px)`
              : `translateY(${(1 - titleProgress) * 50}px) scale(${0.85 + titleProgress * 0.15})`,
            lineHeight: 1.1,
            maxWidth: layout.contentMaxWidth,
          }}
        >
          {content.title || "Project"}
        </div>

        <div
          style={{
            width: lineWidth,
            height: layout.accentBarHeight,
            background: isLeft
              ? theme.colors.accent
              : `linear-gradient(90deg, transparent, ${theme.colors.accent}, transparent)`,
            marginTop: 30,
            borderRadius: layout.accentBarHeight / 2,
          }}
        />

        <div
          style={{
            fontSize: 34,
            fontWeight: 400,
            fontFamily: theme.fonts.body,
            color: theme.colors.textMuted,
            textAlign: isLeft ? "left" : "center",
            marginTop: 25,
            opacity: taglineProgress,
            transform: isLeft
              ? `translateX(${(1 - taglineProgress) * -40}px)`
              : `translateY(${(1 - taglineProgress) * 30}px)`,
            maxWidth: layout.contentMaxWidth,
            lineHeight: 1.4,
          }}
        >
          {content.tagline || ""}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
