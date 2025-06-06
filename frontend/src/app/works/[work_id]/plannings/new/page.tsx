'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';

export default function NewPlanningPage() {
  const { work_id } = useParams() as { work_id: string };
  const router = useRouter();

  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  const handleCreate = async () => {
    if (!title.trim()) {
      alert('기획 제목을 입력해주세요.');
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/works/${work_id}/plannings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plan_title: title,
          plan_content: content,
        }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        console.error('기획 생성 실패:', errorText);
        alert('기획 생성에 실패했습니다.');
        return;
      }

      const result = await res.json();
      console.log('✅ 기획 생성 완료:', result);
      alert('기획이 성공적으로 추가되었습니다.');

      router.push(`/works/${work_id}/plannings`);
    } catch (error) {
      console.error('에러 발생:', error);
      alert('서버 오류로 기획 생성에 실패했습니다.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-bold mb-4">📝 기획 추가</h1>

      <div className="mb-4">
        <label className="block font-medium mb-1">제목</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="기획 제목 입력"
          className="w-full border rounded px-4 py-2"
        />
      </div>

      <div className="mb-6">
        <label className="block font-medium mb-1">내용</label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="기획 내용을 입력하세요"
          className="w-full border rounded px-4 py-2 h-40"
        />
      </div>

      <button
        onClick={handleCreate}
        className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded"
      >
        기획 추가하기
      </button>
    </div>
  );
}
