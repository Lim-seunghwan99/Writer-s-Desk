import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="row-start-2">
        <h1 className="text-4xl font-bold">몬말Easy</h1>
        <p className="text-lg">작가들을 위한 AI 사전 </p>
      </main>
      <footer className="row-start-3 flex gap-6 flex-wrap items-center justify-center">
        <p>copyright 2025. 몬말Easy. All rights reserved.</p>
      </footer>
    </div>
  );
}
