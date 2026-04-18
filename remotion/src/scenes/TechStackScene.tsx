/**
 * RepoReel — Tech Stack Scene
 * Technology badges flowing in with staggered timing.
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

export const TechStackScene: React.FC<{
  content: { technologies?: string[] };
  background_variant?: string;
}> = ({ content, background_variant = "grid" }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const theme = useTheme();

  const techs = content.technologies || [];
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
            marginBottom: 40,
            opacity: titleProgress,
          }}
        >
          Tech Stack
        </div>

        {/* Tech pills grid */}
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 20,
            justifyContent: "center",
            maxWidth: "80%",
          }}
        >
          {techs.map((tech, i) => {
            const delay = 8 + i * 5;
            const progress = spring({
              frame: Math.max(0, frame - delay),
              fps,
              config: { damping: 14, stiffness: 90 },
            });

            // Clean tech name — remove "— evidence: ..." suffixes from analysis
            const cleanTech = tech.split("—")[0].split(" - ")[0].trim();

            return (
              <div
                key={i}
                style={{
                  padding: "16px 36px",
                  borderRadius: 14,
                  backgroundColor: theme.colors.cardBg,
                  border: `2px solid ${theme.colors.accent}40`,
                  color: theme.colors.text,
                  fontSize: 30,
                  fontFamily: theme.fonts.body,
                  fontWeight: 600,
                  opacity: progress,
                  transform: `translateY(${(1 - progress) * 30}px) scale(${0.85 + progress * 0.15})`,
                  boxShadow: `0 4px 20px ${theme.colors.accent}15`,
                }}
              >
                {cleanTech}
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
