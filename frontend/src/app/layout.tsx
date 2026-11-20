import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EduPath AI – Intelligent Learning & Career Ecosystem",
  description: "Learn Smarter. Grow Better. Build Your Career. Integrated AI-powered academic learning, skill mapping, and career preparation platform.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#08060D] text-white antialiased selection:bg-[#8B5CF6] selection:text-white relative">
        {/* Ambient background glow accents */}
        <div className="fixed top-0 left-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[140px] pointer-events-none -z-10" />
        <div className="fixed bottom-10 right-10 w-[600px] h-[600px] bg-purple-900/15 rounded-full blur-[160px] pointer-events-none -z-10" />
        {children}
      </body>
    </html>
  );
}
