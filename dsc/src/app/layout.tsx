import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "ProctorVision - Teacher Dashboard",
  description: "Modern teacher monitoring console for online proctoring exams."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-background text-slate-900 dark:text-slate-100">
        <Script id="theme-init" strategy="beforeInteractive">
          {`
            (() => {
              const stored = window.localStorage.getItem("theme");
              const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
              const theme = stored || (prefersDark ? "dark" : "light");
              document.documentElement.classList.toggle("dark", theme === "dark");
            })();
          `}
        </Script>
        <div className="min-h-screen bg-slate-100 dark:bg-slate-950">
          <div className="w-full px-3 py-4 sm:px-4 lg:px-6">{children}</div>
        </div>
      </body>
    </html>
  );
}
