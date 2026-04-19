/**
 * AutoMotion — Setup / Getting Started Scene
 * Shows installation commands in a terminal-style display.
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

type SetupStep = { command?: string; label?: string };

export const SetupScene: React.FC<{
  content: { steps?: SetupStep[]; title?: string };
  background_variant?: string;
}> = ({ content, background_variant = "grid" }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const theme = useTheme();

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

  const steps = content.steps || [];

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
          {content.title || "Getting Started"}
        </div>

        {/* Terminal window */}
        <div
          style={{
            width: "80%",
            borderRadius: 16,
            overflow: "hidden",
            boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
            border: `1px solid ${theme.colors.accent}30`,
          }}
        >
          {/* Terminal title bar */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: "14px 20px",
              backgroundColor: theme.colors.codeBg,
              borderBottom: `1px solid ${theme.colors.accent}20`,
            }}
          >
            <div style={{ display: "flex", gap: 8 }}>
              <div
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: 6,
                  backgroundColor: "#ff5f57",
                }}
              />
              <div
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: 6,
                  backgroundColor: "#febc2e",
                }}
              />
              <div
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: 6,
                  backgroundColor: "#28c840",
                }}
              />
            </div>
            <span
              style={{
                fontSize: 16,
                color: theme.colors.textMuted,
                fontFamily: theme.fonts.code,
                marginLeft: 8,
              }}
            >
              Terminal
            </span>
          </div>

          {/* Commands */}
          <div
            style={{
              padding: "24px 28px",
              backgroundColor: theme.colors.codeBg,
              fontFamily: theme.fonts.code,
              fontSize: 24,
              lineHeight: 2.2,
            }}
          >
            {steps.slice(0, 4).map((step, i) => {
              const delay = 8 + i * 10;
              const progress = spring({
                frame: Math.max(0, frame - delay),
                fps,
                config: { damping: 14, stiffness: 90 },
              });

              const charsVisible = Math.floor(
                interpolate(
                  frame - delay,
                  [0, Math.max(1, (step.command?.length || 10) * 1.2)],
                  [0, step.command?.length || 0],
                  { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
                ),
              );

              return (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    opacity: progress,
                    transform: `translateY(${(1 - progress) * 15}px)`,
                  }}
                >
                  {step.label && (
                    <span
                      style={{
                        color: theme.colors.textMuted,
                        fontSize: 16,
                        minWidth: 80,
                        textTransform: "uppercase",
                        letterSpacing: "1px",
                      }}
                    >
                      {step.label}
                    </span>
                  )}
                  <span style={{ color: theme.colors.accent }}>$</span>
                  <span style={{ color: theme.colors.codeText }}>
                    {(step.command || "").slice(0, charsVisible)}
                    {charsVisible < (step.command?.length || 0) && (
                      <span
                        style={{
                          color: theme.colors.accent,
                          opacity: frame % 30 < 15 ? 1 : 0,
                        }}
                      >
                        ▋
                      </span>
                    )}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
