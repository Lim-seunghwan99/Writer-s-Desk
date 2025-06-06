'use client';

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

export default function NewEpisodePage() {
  const { work_id } = useParams() as { work_id: string };
  const router = useRouter();

  const [episodeContent, setEpisodeContent] = useState('');

  const handleSubmit = async () => {
    try {
      const res = await fetch(`http://localhost:8000/episodes/${work_id}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          works_id: parseInt(work_id),
          episode_content: episodeContent,
        }),
      });

      if (res.ok) {
        router.push(`/works/${work_id}`);
      } else {
        alert('에피소드 추가 실패');
      }
    } catch (error) {
      console.error('에피소드 추가 에러:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-bold mb-4">에피소드 작성</h1>

      <textarea
        className="w-full p-4 border rounded mb-4"
        placeholder="에피소드 내용을 입력하세요..."
        rows={10}
        value={episodeContent}
        onChange={(e) => setEpisodeContent(e.target.value)}
      />

      <div className="flex gap-4">
        <button
          onClick={handleSubmit}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          저장
        </button>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
        >
          취소
        </button>
      </div>
    </div>
  );
}
