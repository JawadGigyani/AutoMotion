/**
 * AutoMotion — Theme Context Provider
 */
import React, { createContext, useContext } from "react";
import { Theme, darkCinematic } from "./index";

const ThemeContext = createContext<Theme>(darkCinematic);

export const ThemeProvider: React.FC<{
  theme: Theme;
  children: React.ReactNode;
}> = ({ theme, children }) => {
  return (
    <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>
  );
};

export const useTheme = (): Theme => useContext(ThemeContext);
