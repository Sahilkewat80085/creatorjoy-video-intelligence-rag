import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const viewport: Viewport = {
  themeColor: "#0a0a0f",
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: "Creator Intelligence AI - Video Comparison & RAG Analytics",
  description:
    "Compare YouTube and Instagram video content using RAG-powered AI. Ingest video transcripts, analyze audience engagement, and query insights in real-time.",
  keywords: ["Creator Intelligence", "RAG R&D", "FastAPI", "NextJS", "Qdrant", "Speech-to-Text", "Whisper", "Gemini AI"],
  robots: "index, follow",
  openGraph: {
    title: "Creator Intelligence AI - Video RAG Analyzer",
    description: "Real-time RAG-powered video content comparison and audience analytics.",
    type: "website",
    url: "https://creatorjoy-video-intelligence-rag.vercel.app",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable} style={{ colorScheme: "dark" }}>
      <body className={`${inter.className} antialiased bg-[#0a0a0f] text-zinc-100 min-h-screen selection:bg-violet-500/30 selection:text-white`}>
        {children}
      </body>
    </html>
  );
}

