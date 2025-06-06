// components/WordCardWithExamples.tsx
"use client";

import { useState } from "react";
import Link from "next/link";

interface Example {
  word_example_content: string;
  example_sequence: number;
}

interface Word {
  words_id: number;
  word_name: string;
  word_content: string;
  user_id: string;
  word_created_time: string;
  word_count: number;
  examples: Example[];
}

interface Props {
  word: Word;
}

export default function WordCardWithExamples({ word }: Props) {
  const [exampleInput, setExampleInput] = useState("");
  const [examples, setExamples] = useState<Example[]>(word.examples || []);
  const [isAdding, setIsAdding] = useState(false);

  const handleAddExample = async () => {
    if (!exampleInput.trim()) {
      alert("예문을 입력해주세요");
      return;
    }
    try {
      const res = await fetch(`http://localhost:8000/words/${word.words_id}/examples`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ word_example_content: exampleInput }),
      });
      if (!res.ok) throw new Error("예문 추가 실패");
      const data = await res.json();
      setExamples((prev) => [...prev, data]);
      setExampleInput("");
      setIsAdding(false);
      alert("예문이 추가되었습니다");
    } catch (err) {
      console.error("예문 추가 오류:", err);
      alert("예문 추가에 실패했습니다");
    }
  };

  return (
    <div className="border p-4 rounded shadow-sm">
      <Link href={`/word/${word.user_id}/${word.words_id}`}>
        <div className="cursor-pointer hover:bg-gray-50 rounded p-2 transition">
          <h3 className="text-xl font-bold">{word.word_name}</h3>
          <p className="text-sm text-gray-600 mb-2">{word.word_content}</p>

          <div className="mb-2">
            <h4 className="font-semibold">📌 예문</h4>
            {examples.length === 0 ? (
              <p className="text-gray-400 text-sm">예문이 없습니다.</p>
            ) : (
              <ul className="list-disc list-inside text-sm">
                {examples.map((ex, idx) => (
                  <li key={idx}>{ex.word_example_content}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </Link>

      {isAdding ? (
        <div className="space-y-2 mt-4">
          <input
            type="text"
            value={exampleInput}
            onChange={(e) => setExampleInput(e.target.value)}
            placeholder="예문을 입력하세요"
            className="w-full px-3 py-2 border rounded"
          />
          <div className="flex gap-2">
            <button
              onClick={handleAddExample}
              className="bg-green-500 text-white px-4 py-1 rounded"
            >
              추가
            </button>
            <button
              onClick={() => {
                setExampleInput("");
                setIsAdding(false);
              }}
              className="bg-gray-300 px-4 py-1 rounded"
            >
              취소
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setIsAdding(true)}
          className="text-blue-500 text-sm underline mt-2"
        >
          + 예문 추가하기
        </button>
      )}
    </div>
  );
}
