"use client";

import { useEffect, useState } from "react";
import { FiMoon, FiSun } from "react-icons/fi";

export const ThemeToggle = () => {
  const [isDark, setIsDark] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    setIsDark(document.documentElement.classList.contains("dark"));
  }, []);

  const toggleTheme = () => {
    const nextIsDark = !isDark;
    document.documentElement.classList.toggle("dark", nextIsDark);
    window.localStorage.setItem("theme", nextIsDark ? "dark" : "light");
    setIsDark(nextIsDark);
  };

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-950/70 dark:text-slate-300 dark:hover:bg-slate-900"
      aria-label="Toggle theme"
    >
      {mounted && isDark ? <FiSun className="h-4 w-4" /> : <FiMoon className="h-4 w-4" />}
      <span className="hidden sm:inline">{mounted && isDark ? "Light mode" : "Dark mode"}</span>
    </button>
  );
};
