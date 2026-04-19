/**
 * AutoMotion — Tech Stack Scene
 * Technology badges with staggered animation. Card shape varies per theme.
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

const CARD_RADIUS: Record<string, number> = {
  rounded: 14,
  sharp: 3,
  pill: 50,
};

export const TechStackScene: React.FC<{
  content: { technologies?: string[] };
  background_variant?: string;
}> = ({ content, background_variant = "grid" }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const theme = useTheme();
  const { layout } = theme;

  const techs = content.technologies || [];
  const titleProgress = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 80 },
  });

  const exitStart = Math.max(0, durationInFrames - 10);
  const exitOpacity = interpolate(
    frame,
    [exitStart, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const radius = CARD_RADIUS[layout.cardStyle] ?? 14;

  const labelStyle: React.CSSProperties = {
    fontSize: 28,
    fontWeight: 600,
    fontFamily: theme.fonts.body,
    color: theme.colors.accent,
    letterSpacing: layout.sectionLabelStyle === "uppercase" ? "4px" : "1px",
    textTransform: layout.sectionLabelStyle === "none" ? undefined : layout.sectionLabelStyle,
    marginBottom: 40,
    opacity: titleProgress,
  };

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
        <div style={labelStyle}>
          {layout.sectionLabelStyle === "none" ? "> tech_stack" : "Tech Stack"}
        </div>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 20,
            justifyContent: "center",
            maxWidth: layout.contentMaxWidth,
          }}
        >
          {techs.map((tech, i) => {
            const delay = 8 + i * 5;
            const progress = spring({
              frame: Math.max(0, frame - delay),
              fps,
              config: { damping: 14, stiffness: 90 },
            });

            const cleanTech = tech.split("—")[0].split(" - ")[0].trim();

            return (
              <div
                key={i}
                style={{
                  padding: "16px 36px",
                  borderRadius: radius,
                  backgroundColor: theme.colors.cardBg,
                  border: `${layout.cardBorderWidth}px solid ${theme.colors.accent}40`,
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
