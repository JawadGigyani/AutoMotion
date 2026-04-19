/**
 * AutoMotion — Title Scene
 * Project name with tagline, animated accent line.
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

  const titleProgress = spring({ frame, fps, config: { damping: 14, stiffness: 80 } });
  const taglineProgress = spring({
    frame: Math.max(0, frame - 12),
    fps,
    config: { damping: 16, stiffness: 70 },
  });
  const lineWidth = interpolate(titleProgress, [0, 1], [0, 120]);

  // Exit fade
  const exitStart = Math.max(0, durationInFrames - 10);
  const exitOpacity = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <NoiseBackground variant={background_variant as any} />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: "center",
          padding: 80,
          opacity: exitOpacity,
        }}
      >
        {/* Title */}
        <div
          style={{
            fontSize: 82,
            fontWeight: 800,
            fontFamily: theme.fonts.heading,
            color: theme.colors.text,
            textAlign: "center",
            letterSpacing: "-2px",
            opacity: titleProgress,
            transform: `translateY(${(1 - titleProgress) * 50}px) scale(${0.85 + titleProgress * 0.15})`,
            lineHeight: 1.1,
            maxWidth: "90%",
          }}
        >
          {content.title || "Project"}
        </div>

        {/* Accent line */}
        <div
          style={{
            width: lineWidth,
            height: 4,
            background: `linear-gradient(90deg, transparent, ${theme.colors.accent}, transparent)`,
            marginTop: 30,
            borderRadius: 2,
          }}
        />

        {/* Tagline */}
        <div
          style={{
            fontSize: 34,
            fontWeight: 400,
            fontFamily: theme.fonts.body,
            color: theme.colors.textMuted,
            textAlign: "center",
            marginTop: 25,
            opacity: taglineProgress,
            transform: `translateY(${(1 - taglineProgress) * 30}px)`,
            maxWidth: "80%",
            lineHeight: 1.4,
          }}
        >
          {content.tagline || ""}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
