/**
 * AutoMotion — Code Highlight Scene
 * Shows a real code snippet from the repo in a VS Code-styled editor.
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
import { CodeBlock } from "../components/CodeBlock";

export const CodeHighlightScene: React.FC<{
  content: { filename?: string; code_snippet?: string; caption?: string };
  background_variant?: string;
}> = ({ content, background_variant = "dots" }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const theme = useTheme();

  const containerProgress = spring({
    frame,
    fps,
    config: { damping: 16, stiffness: 70 },
  });

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
          padding: 60,
          opacity: exitOpacity,
        }}
      >
        <div
          style={{
            opacity: containerProgress,
            transform: `translateY(${(1 - containerProgress) * 40}px) scale(${0.92 + containerProgress * 0.08})`,
            width: "100%",
            display: "flex",
            justifyContent: "center",
          }}
        >
          <CodeBlock
            code={content.code_snippet || "// No code available"}
            filename={content.filename || "code.ts"}
            caption={content.caption}
          />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
