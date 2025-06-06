'use client';

import { useState } from 'react';

interface EasyExampleModalProps {
  onClose: () => void;
}

export default function EasyExampleModal({ onClose }: EasyExampleModalProps) {
  const [word, setWord] = useState('');
  const [loading, setLoading] = useState(false);
  const [easyMeaning, setEasyMeaning] = useState('');

  const fetchExample = async () => {
    if (!word.trim()) {
      alert("단어를 입력하세요.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/words/generate/${word}/easy`);
      const data = await res.json();
      setEasyMeaning(data.easy_meaning);
    } catch (error) {
      console.error("설명 생성 실패:", error);
      alert("설명을 생성하지 못했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">설명 생성</h2>

        <input
          type="text"
          placeholder="단어를 입력하세요"
          className="w-full border px-3 py-2 mb-4"
          value={word}
          onChange={(e) => setWord(e.target.value)}
        />

        <button
          onClick={fetchExample}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          disabled={loading}
        >
          {loading ? '생성 중...' : '설명 생성'}
        </button>

        {easyMeaning && (
          <div className="mt-4 p-3 bg-gray-100 border rounded text-gray-800">
            <strong>설명:</strong> {easyMeaning}
          </div>
        )}

        <div className="mt-6 text-right">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
}
