// components/WordExampleItem.tsx
"use client";

import { useState } from "react";

interface Props {
  wordId: number;
  example: {
    word_example_content: string;
    example_sequence: number;
  };
  onUpdate: (newContent: string) => void;
}

export default function WordExampleItem({ wordId, example, onUpdate }: Props) {
  const [isEditing, setIsEditing] = useState(false);
  const [content, setContent] = useState(example.word_example_content);
  const [hovered, setHovered] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleUpdate = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `http://localhost:8000/words/${wordId}/examples/${example.example_sequence}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ word_example_content: content }),
        }
      );
      if (!res.ok) throw new Error("수정 실패");
      onUpdate(content);
      setIsEditing(false);
    } catch (err) {
      alert("예문 수정 실패");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    const confirmed = window.confirm("정말 삭제하시겠습니까?");
    if (!confirmed) return;
    try {
      const res = await fetch(
        `http://localhost:8000/words/${wordId}/examples/${example.example_sequence}`,
        {
          method: "DELETE",
        }
      );
      if (!res.ok) throw new Error("삭제 실패");
      onUpdate(""); // 빈 문자열로 반환하여 상위에서 삭제 처리
    } catch (err) {
      alert("예문 삭제 실패");
    }
  };

  return (
    <div
      className="relative"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {!isEditing ? (
        <div className="flex items-center justify-between">
          <span>{example.word_example_content}</span>
          {hovered && (
            <div className="flex gap-2 ml-2">
              <button
                onClick={() => setIsEditing(true)}
                className="text-xs text-blue-500 underline"
              >
                수정하기
              </button>
              <button
                onClick={handleDelete}
                className="text-xs text-red-500 underline"
              >
                삭제하기
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="flex gap-2 items-center">
          <input
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="border px-2 py-1 rounded text-sm w-full"
          />
          <button
            onClick={handleUpdate}
            disabled={loading}
            className="text-sm bg-blue-500 text-white px-2 py-1 rounded"
          >
            저장
          </button>
          <button
            onClick={() => setIsEditing(false)}
            className="text-sm text-gray-500 px-2 py-1"
          >
            취소
          </button>
        </div>
      )}
    </div>
  );
}
