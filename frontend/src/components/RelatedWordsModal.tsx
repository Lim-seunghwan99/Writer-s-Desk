// components/RelatedWordsModal.tsx
"use client";

import { useEffect, useState } from "react";

interface RelatedWord {
  form: string;
  korean_definition?: string;
  english_definition?: string;
  score?: number;
}

interface Props {
  targetWord: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function RelatedWordsModal({ targetWord, isOpen, onClose }: Props) {
  const [relatedWords, setRelatedWords] = useState<RelatedWord[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!isOpen || !targetWord) return;
    setIsLoading(true);
    fetch(`http://localhost:8000/words/${encodeURIComponent(targetWord)}/relate/open_search?limit=10`)
      .then((res) => res.json())
      .then((data) => setRelatedWords(data))
      .catch((err) => console.error("유사 단어 불러오기 실패:", err))
      .finally(() => setIsLoading(false));
  }, [isOpen, targetWord]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-xl p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-2 right-2 text-gray-500 hover:text-black"
        >
          ✕
        </button>

        <h2 className="text-xl font-bold mb-4">
          🔍 "{targetWord}" 와 유사한 단어
        </h2>

        {isLoading ? (
          <p className="text-gray-500">불러오는 중...</p>
        ) : relatedWords.length === 0 ? (
          <p className="text-gray-500">유사 단어가 없습니다.</p>
        ) : (
          <ul className="space-y-2 text-sm">
            {relatedWords.map((word, idx) => (
              <li key={idx}>
                <strong>{word.form}</strong>
                {word.korean_definition && ` - ${word.korean_definition}`}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
