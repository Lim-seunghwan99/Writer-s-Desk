import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Providers from "@/components/Providers";
import { SessionProvider } from "next-auth/react";
import Modebtn from "@/components/Modebtn";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "몬말Easy | 작가들을 위한 AI 사전",
  description: "Metaverse academy 4th project page",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    
    
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-white`}
      >
        <Providers>
            <Navbar />
            <Modebtn />
          <main className="flex-grow w-full max-w-5xl mx-auto px-4 py-8">
            {children}
          </main>
          <footer className="py-4 text-center text-sm text-gray-400">
            ⓒ 2025 몬말Easy 프로젝트
          </footer>
        </Providers>
      </body>
    </html>
  );
}
