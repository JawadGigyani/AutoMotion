/**
 * RepoReel — Theme Type Definitions & All Theme Data
 */

export type ThemeColors = {
  bgPrimary: string;
  bgSecondary: string;
  bgGradient: string;
  accent: string;
  accentSecondary: string;
  text: string;
  textMuted: string;
  codeBg: string;
  codeText: string;
  cardBg: string;
};

export type ThemeFonts = {
  heading: string;
  body: string;
  code: string;
};

export type Theme = {
  id: string;
  name: string;
  colors: ThemeColors;
  fonts: ThemeFonts;
};

// ── Dark Cinematic ──
export const darkCinematic: Theme = {
  id: "dark_cinematic",
  name: "Dark Cinematic",
  colors: {
    bgPrimary: "#0a0a0a",
    bgSecondary: "#1a1a2e",
    bgGradient: "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)",
    accent: "#6c63ff",
    accentSecondary: "#a78bfa",
    text: "#f0f0f0",
    textMuted: "#8b8b9e",
    codeBg: "#1e1e2e",
    codeText: "#cdd6f4",
    cardBg: "#16162a",
  },
  fonts: { heading: "Inter", body: "Inter", code: "'JetBrains Mono'" },
};

// ── Neon Cyberpunk ──
export const neonCyberpunk: Theme = {
  id: "neon_cyberpunk",
  name: "Neon Cyberpunk",
  colors: {
    bgPrimary: "#0d0221",
    bgSecondary: "#150530",
    bgGradient: "linear-gradient(135deg, #0d0221 0%, #150530 50%, #0a0118 100%)",
    accent: "#ff00ff",
    accentSecondary: "#00ffff",
    text: "#f0e6ff",
    textMuted: "#9b72cf",
    codeBg: "#1a0030",
    codeText: "#e0d0ff",
    cardBg: "#120428",
  },
  fonts: { heading: "Inter", body: "Inter", code: "'JetBrains Mono'" },
};

// ── Minimal Light ──
export const minimalLight: Theme = {
  id: "minimal_light",
  name: "Minimal Light",
  colors: {
    bgPrimary: "#f8f9fa",
    bgSecondary: "#e9ecef",
    bgGradient: "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)",
    accent: "#3b82f6",
    accentSecondary: "#1d4ed8",
    text: "#1a1a2e",
    textMuted: "#6b7280",
    codeBg: "#1e293b",
    codeText: "#e2e8f0",
    cardBg: "#ffffff",
  },
  fonts: { heading: "Inter", body: "Inter", code: "'JetBrains Mono'" },
};

// ── Terminal Green ──
export const terminalGreen: Theme = {
  id: "terminal_green",
  name: "Terminal Green",
  colors: {
    bgPrimary: "#0c0c0c",
    bgSecondary: "#0a1a0a",
    bgGradient: "linear-gradient(135deg, #0c0c0c 0%, #0a1a0a 100%)",
    accent: "#00ff41",
    accentSecondary: "#39ff14",
    text: "#00ff41",
    textMuted: "#007a1f",
    codeBg: "#0a1a0a",
    codeText: "#00ff41",
    cardBg: "#0d1a0d",
  },
  fonts: { heading: "'JetBrains Mono'", body: "'JetBrains Mono'", code: "'JetBrains Mono'" },
};

// ── Ocean Depth ──
export const oceanDepth: Theme = {
  id: "ocean_depth",
  name: "Ocean Depth",
  colors: {
    bgPrimary: "#0a192f",
    bgSecondary: "#112240",
    bgGradient: "linear-gradient(135deg, #0a192f 0%, #112240 100%)",
    accent: "#64ffda",
    accentSecondary: "#7ee8fa",
    text: "#ccd6f6",
    textMuted: "#8892b0",
    codeBg: "#0a192f",
    codeText: "#a8b2d1",
    cardBg: "#112240",
  },
  fonts: { heading: "Inter", body: "Inter", code: "'JetBrains Mono'" },
};

// ── Lookup ──
const THEMES: Record<string, Theme> = {
  dark_cinematic: darkCinematic,
  neon_cyberpunk: neonCyberpunk,
  minimal_light: minimalLight,
  terminal_green: terminalGreen,
  ocean_depth: oceanDepth,
};

export function getTheme(id: string): Theme {
  return THEMES[id] || darkCinematic;
}
