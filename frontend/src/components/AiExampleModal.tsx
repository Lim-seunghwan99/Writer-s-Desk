// components/AiExampleModal.tsx
"use client";

import { useState } from "react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export default function AiExampleModal({ isOpen, onClose }: Props) {
  const [input, setInput] = useState("");
  const [examples, setExamples] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!input.trim()) return alert("단어를 입력해주세요.");
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/words/${encodeURIComponent(input)}/ai_word_example`, {
        method: "POST",
      });
      const data = await res.json();
      setExamples(data.examples || []);
    } catch (err) {
      alert("AI 예문 생성 실패");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded shadow-lg w-full max-w-md relative">
        <button onClick={onClose} className="absolute top-2 right-2 text-gray-400 hover:text-black">
          ✕
        </button>
        <h2 className="text-xl font-bold mb-4">🤖 AI 예문 생성</h2>
        <input
          type="text"
          placeholder="예문 생성할 단어 입력"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="w-full px-3 py-2 rounded border mb-3"
        />
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full bg-purple-600 text-white px-4 py-2 rounded"
        >
          {loading ? "생성 중..." : "AI 예문 생성"}
        </button>

        {examples.length > 0 && (
          <div className="mt-4">
            <h3 className="font-semibold mb-2">생성된 예문</h3>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              {examples.map((ex, i) => (
                <li key={i}>{ex}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
