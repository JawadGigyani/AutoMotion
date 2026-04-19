/**
 * AutoMotion — Overview Scene
 * Project description with metadata badges. Adapts to theme layout.
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
import { Badge } from "../components/Badge";

export const OverviewScene: React.FC<{
  content: { description?: string; badges?: string[] };
  background_variant?: string;
}> = ({ content, background_variant = "noise" }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const theme = useTheme();
  const { layout } = theme;

  const textProgress = spring({
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

  const badges = content.badges || [];
  const isLeft = layout.titleAlign === "left";

  return (
    <AbsoluteFill>
      <NoiseBackground variant={background_variant as any} />
      <AbsoluteFill
        style={{
          justifyContent: "center",
          alignItems: isLeft ? "flex-start" : "center",
          padding: isLeft ? "80px 120px" : 100,
          opacity: exitOpacity,
        }}
      >
        <div
          style={{
            fontSize: 42,
            fontWeight: 400,
            fontFamily: theme.fonts.body,
            color: theme.colors.text,
            textAlign: isLeft ? "left" : "center",
            lineHeight: 1.6,
            opacity: textProgress,
            transform: isLeft
              ? `translateX(${(1 - textProgress) * -40}px)`
              : `translateY(${(1 - textProgress) * 40}px)`,
            maxWidth: layout.contentMaxWidth,
          }}
        >
          {content.description || "An open source project."}
        </div>

        {badges.length > 0 && (
          <div
            style={{
              display: "flex",
              gap: 16,
              marginTop: 40,
              flexWrap: "wrap",
              justifyContent: isLeft ? "flex-start" : "center",
            }}
          >
            {badges.map((badge, i) => (
              <Badge key={i} text={badge} index={i} />
            ))}
          </div>
        )}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
