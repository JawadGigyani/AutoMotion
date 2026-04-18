/**
 * RepoReel — Remotion Root
 * Registers the RepoReel composition with calculateMetadata for dynamic duration.
 */
import React from "react";
import { Composition } from "remotion";
import { RepoReelVideo, RepoReelVideoProps } from "./RepoReelVideo";
import { darkCinematic } from "./themes/index";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="RepoReel"
      component={RepoReelVideo}
      durationInFrames={300}
      fps={30}
      width={1920}
      height={1080}
      defaultProps={{
        scenes: [
          {
            narration: "Welcome to RepoReel",
            visual_type: "title",
            content: { title: "RepoReel", tagline: "AI-powered repo explainers" },
            animation: "fade_in",
            background_variant: "gradient",
            start: 0,
            durationInFrames: 150,
          },
          {
            narration: "Turn any GitHub repository into a video",
            visual_type: "overview",
            content: {
              description: "Paste a GitHub URL and get a narrated explainer video.",
              badges: ["AI", "Video", "GitHub"],
            },
            animation: "slide_up",
            background_variant: "noise",
            start: 150,
            durationInFrames: 150,
          },
        ],
        audioUrl: "",
        totalFrames: 300,
        fps: 30,
        theme: darkCinematic,
      }}
      calculateMetadata={({ props }: { props: RepoReelVideoProps }) => {
        return {
          durationInFrames: props.totalFrames || 300,
          fps: props.fps || 30,
        };
      }}
    />
  );
};
