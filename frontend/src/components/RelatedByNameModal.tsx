// components/RelatedByNameModal.tsx
"use client";

import { useState } from "react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export default function RelatedByNameModal({ isOpen, onClose }: Props) {
  const [input, setInput] = useState("");
  const [related, setRelated] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!input.trim()) return alert("단어를 입력해주세요.");
    setLoading(true);
    try {
      const res = await fetch(
        `http://localhost:8000/words/words/${encodeURIComponent(input)}/related`
      );
      const data = await res.json();
      setRelated(data.related_words || []);
    } catch (err) {
      alert("관련 단어 검색 실패");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded shadow-lg w-full max-w-md relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-black"
        >
          ✕
        </button>
        <h2 className="text-xl font-bold mb-4">🔗 단어 기반 관련어 찾기</h2>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="예: 사과"
          className="w-full px-3 py-2 border rounded mb-4"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="w-full bg-blue-500 text-white px-4 py-2 rounded"
        >
          {loading ? "불러오는 중..." : "관련 단어 검색"}
        </button>

        {related.length > 0 && (
          <div className="mt-4">
            <h3 className="font-semibold mb-2">관련 단어</h3>
            <ul className="list-disc pl-5 text-sm space-y-1">
              {related.map((word, i) => (
                <li key={i}>{word}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
