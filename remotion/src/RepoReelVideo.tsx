/**
 * RepoReel — Main Video Composition
 * Orchestrates all scenes using TransitionSeries with Audio.
 */
import React from "react";
import { AbsoluteFill, Audio } from "remotion";
import {
  TransitionSeries,
  linearTiming,
} from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadJetBrains } from "@remotion/google-fonts/JetBrainsMono";

import { Theme, getTheme } from "./themes/index";
import { ThemeProvider } from "./themes/ThemeProvider";

import { TitleScene } from "./scenes/TitleScene";
import { OverviewScene } from "./scenes/OverviewScene";
import { TechStackScene } from "./scenes/TechStackScene";
import { CodeHighlightScene } from "./scenes/CodeHighlightScene";
import { FeaturesScene } from "./scenes/FeaturesScene";
import { StatsScene } from "./scenes/StatsScene";
import { ClosingScene } from "./scenes/ClosingScene";

// Load fonts
loadInter();
loadJetBrains();

// ── Scene type → component mapping ──
const SCENE_COMPONENTS: Record<string, React.FC<any>> = {
  title: TitleScene,
  overview: OverviewScene,
  tech_stack: TechStackScene,
  code_highlight: CodeHighlightScene,
  features: FeaturesScene,
  stats: StatsScene,
  closing: ClosingScene,
};

// ── Props type ──
export type SceneData = {
  narration: string;
  visual_type: string;
  content: Record<string, any>;
  animation: string;
  background_variant: string;
  start: number;
  durationInFrames: number;
};

export type RepoReelVideoProps = {
  scenes: SceneData[];
  audioUrl: string;
  totalFrames: number;
  fps: number;
  theme: Theme | { id: string };
};

/**
 * Main video composition.
 * Maps scene data to themed components via TransitionSeries, embeds audio.
 */
export const RepoReelVideo: React.FC<RepoReelVideoProps> = ({
  scenes,
  audioUrl,
  theme: themeProp,
}) => {
  // Resolve theme
  const theme: Theme =
    "colors" in themeProp
      ? (themeProp as Theme)
      : getTheme((themeProp as { id: string }).id);

  const transitionDuration = 12; // frames (0.4s at 30fps)

  return (
    <ThemeProvider theme={theme}>
      <AbsoluteFill style={{ backgroundColor: theme.colors.bgPrimary }}>
        {/* Audio track */}
        {audioUrl && <Audio src={audioUrl} volume={1} />}

        {/* Scene sequence with transitions */}
        <TransitionSeries>
          {scenes.map((scene, i) => {
            const SceneComponent =
              SCENE_COMPONENTS[scene.visual_type] || OverviewScene;

            return (
              <React.Fragment key={i}>
                <TransitionSeries.Sequence
                  durationInFrames={scene.durationInFrames}
                >
                  <SceneComponent
                    content={scene.content}
                    background_variant={scene.background_variant}
                  />
                </TransitionSeries.Sequence>

                {/* Add transition between scenes (not after last) */}
                {i < scenes.length - 1 && (
                  <TransitionSeries.Transition
                    presentation={fade()}
                    timing={linearTiming({
                      durationInFrames: transitionDuration,
                    })}
                  />
                )}
              </React.Fragment>
            );
          })}
        </TransitionSeries>
      </AbsoluteFill>
    </ThemeProvider>
  );
};
