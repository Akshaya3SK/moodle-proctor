import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ProctorVision – Teacher Dashboard",
  description: "Modern teacher monitoring console for online proctoring exams."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-slate-100">
        <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900">
          <div className="mx-auto max-w-7xl px-3 sm:px-4 lg:px-6 py-4">
            {children}
          </div>
        </div>
      </body>
    </html>
  );
}

