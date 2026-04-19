/**
 * AutoMotion — Features Scene
 * Feature cards with staggered animation. Shape/style varies per theme.
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

type Feature = { title?: string; description?: string };

const CARD_RADIUS: Record<string, number> = {
  rounded: 14,
  sharp: 3,
  pill: 24,
};

export const FeaturesScene: React.FC<{
  content: { features?: (Feature | string)[] };
  background_variant?: string;
}> = ({ content, background_variant = "radial" }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const theme = useTheme();
  const { layout } = theme;

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

  const features = (content.features || []).map((f) => {
    if (typeof f === "string") return { title: f, description: "" };
    return f;
  });

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
          {layout.sectionLabelStyle === "none" ? "> features" : "Key Features"}
        </div>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 20,
            width: layout.contentMaxWidth,
          }}
        >
          {features.slice(0, 4).map((feature, i) => {
            const delay = 6 + i * 6;
            const progress = spring({
              frame: Math.max(0, frame - delay),
              fps,
              config: { damping: 15, stiffness: 90 },
            });

            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 20,
                  padding: "20px 30px",
                  borderRadius: radius,
                  backgroundColor: `${theme.colors.cardBg}cc`,
                  border: `${layout.cardBorderWidth}px solid ${theme.colors.accent}25`,
                  opacity: progress,
                  transform: `translateX(${(1 - progress) * -60}px)`,
                }}
              >
                <div
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: layout.cardStyle === "sharp" ? 2 : 5,
                    backgroundColor: theme.colors.accent,
                    flexShrink: 0,
                  }}
                />
                <div>
                  <div
                    style={{
                      fontSize: 28,
                      fontWeight: 600,
                      fontFamily: theme.fonts.body,
                      color: theme.colors.text,
                    }}
                  >
                    {feature.title || "Feature"}
                  </div>
                  {feature.description && (
                    <div
                      style={{
                        fontSize: 20,
                        fontFamily: theme.fonts.body,
                        color: theme.colors.textMuted,
                        marginTop: 4,
                      }}
                    >
                      {feature.description}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
