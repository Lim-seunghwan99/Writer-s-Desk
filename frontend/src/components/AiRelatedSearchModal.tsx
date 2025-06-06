// components/AiRelatedSearchModal.tsx
"use client";

import { useState } from "react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export default function AiRelatedSearchModal({ isOpen, onClose }: Props) {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isResultVisible, setIsResultVisible] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) {
      alert("단어를 입력해주세요");
      return;
    }
    setIsLoading(true);
    setIsResultVisible(false);
    try {
      const res = await fetch("http://localhost:8000/words/find-related", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, target_word_count: 5 }),
      });
      const data = await res.json();

      if (Array.isArray(data.final_words) && data.final_words.length > 0) {
      setResult(data.final_words);
      }else{
        setResult([]);
      }

      setIsResultVisible(true);

    } catch (err) {
      console.error("AI 단어 추천 오류:", err);
      alert("AI 단어 추천 실패");
      setResult([]);
      setIsResultVisible(true);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md relative">
        <button onClick={onClose} className="absolute top-2 right-2 text-gray-500 hover:text-black">✕</button>
        <h2 className="text-xl font-bold mb-4">🤖 AI 단어 추천 검색</h2>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="유사 단어를 추천받을 단어 입력"
          className="w-full px-3 py-2 border rounded mb-4"
        />

        <button
          onClick={handleSearch}
          className="bg-purple-600 text-white px-4 py-2 rounded w-full mb-4"
        >
          AI 유사 단어 검색
        </button>

        {isLoading && <p className="text-sm text-gray-500">불러오는 중...</p>}

        {isResultVisible && (
          <div className="mt-2">
            {result.length > 0 ? (
              <ul className="list-disc list-inside space-y-1 text-sm">
                {result.map((word, idx) => (
                  <li key={idx}>{word}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">추천된 단어가 없습니다.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
