/**
 * AutoMotion — Features Scene
 * Feature cards sliding in with staggered timing.
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

export const FeaturesScene: React.FC<{
  content: { features?: (Feature | string)[] };
  background_variant?: string;
}> = ({ content, background_variant = "radial" }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const theme = useTheme();

  const titleProgress = spring({ frame, fps, config: { damping: 15, stiffness: 80 } });

  const exitStart = Math.max(0, durationInFrames - 10);
  const exitOpacity = interpolate(frame, [exitStart, durationInFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Normalize features — can be string[] or {title, description}[]
  const features = (content.features || []).map((f) => {
    if (typeof f === "string") return { title: f, description: "" };
    return f;
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
          Key Features
        </div>

        {/* Feature cards */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 20,
            width: "80%",
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
                  borderRadius: 14,
                  backgroundColor: `${theme.colors.cardBg}cc`,
                  border: `1px solid ${theme.colors.accent}25`,
                  opacity: progress,
                  transform: `translateX(${(1 - progress) * -60}px)`,
                }}
              >
                {/* Accent dot */}
                <div
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: 5,
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
