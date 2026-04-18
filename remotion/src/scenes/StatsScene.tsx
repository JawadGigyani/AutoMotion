/**
 * RepoReel — Stats Scene
 * Animated counters for stars, forks, language breakdown.
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
import { AnimatedCounter } from "../components/AnimatedCounter";

export const StatsScene: React.FC<{
  content: {
    stars?: number;
    forks?: number;
    language?: string;
    contributors?: number;
    languages?: Record<string, number>;
  };
  background_variant?: string;
}> = ({ content, background_variant = "dots" }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const theme = useTheme();

  const titleProgress = spring({ frame, fps, config: { damping: 15, stiffness: 80 } });

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
        {/* Section title */}
        <div
          style={{
            fontSize: 28,
            fontWeight: 600,
            fontFamily: theme.fonts.body,
            color: theme.colors.accent,
            textTransform: "uppercase",
            letterSpacing: "4px",
            marginBottom: 50,
            opacity: titleProgress,
          }}
        >
          Community
        </div>

        {/* Stat counters row */}
        <div
          style={{
            display: "flex",
            gap: 80,
            justifyContent: "center",
            alignItems: "flex-start",
          }}
        >
          {content.stars !== undefined && content.stars > 0 && (
            <AnimatedCounter
              value={content.stars}
              label="Stars"
              suffix=""
              delay={5}
            />
          )}
          {content.forks !== undefined && content.forks > 0 && (
            <AnimatedCounter
              value={content.forks}
              label="Forks"
              suffix=""
              delay={12}
            />
          )}
          {content.contributors !== undefined && content.contributors > 0 && (
            <AnimatedCounter
              value={content.contributors}
              label="Contributors"
              suffix=""
              delay={19}
            />
          )}
        </div>

        {/* Primary language badge */}
        {content.language && (
          <div
            style={{
              marginTop: 50,
              display: "flex",
              alignItems: "center",
              gap: 12,
              opacity: interpolate(frame, [20, 35], [0, 1], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }),
            }}
          >
            <div
              style={{
                width: 14,
                height: 14,
                borderRadius: 7,
                backgroundColor: theme.colors.accent,
              }}
            />
            <span
              style={{
                fontSize: 28,
                fontFamily: theme.fonts.body,
                color: theme.colors.text,
                fontWeight: 500,
              }}
            >
              {content.language}
            </span>
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
