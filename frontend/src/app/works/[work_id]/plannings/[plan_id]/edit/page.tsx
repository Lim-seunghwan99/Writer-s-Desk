'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function EditPlanningPage() {
  const { work_id, plan_id } = useParams() as {
    work_id: string;
    plan_id: string;
  };

  const router = useRouter();

  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);

  // 기존 데이터 불러오기
  const fetchPlanning = async () => {
    try {
      const res = await fetch(`http://localhost:8000/works/${work_id}/plannings/${plan_id}`);
      if (!res.ok) throw new Error('기획 정보를 불러올 수 없습니다.');
      const data = await res.json();
      setTitle(data.plan_title || '');
      setContent(data.plan_content || '');
    } catch (err) {
      console.error('불러오기 실패:', err);
      alert('기획 정보를 불러오는 데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    if (!title.trim()) {
      alert('제목을 입력해주세요.');
      return;
    }

    try {
      const res = await fetch(
        `http://localhost:8000/works/${work_id}/plannings/${plan_id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            plan_title: title,
            plan_content: content,
          }),
        }
      );

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText);
      }

      alert('📘 기획이 수정되었습니다!');
      router.push(`/works/${work_id}/plannings`);
    } catch (err) {
      console.error('수정 실패:', err);
      alert('기획 수정 실패');
    }
  };

  useEffect(() => {
    fetchPlanning();
  }, [work_id, plan_id]);

  if (loading) return <div className="p-6">로딩 중...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6 space-y-4">
      <h1 className="text-2xl font-bold mb-4">✏️ 기획 수정</h1>

      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="기획 제목"
        className="w-full border p-2 rounded mb-2"
      />
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="기획 내용"
        className="w-full h-40 border p-2 rounded"
      />

      <button
        onClick={handleUpdate}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        저장
      </button>
    </div>
  );
}
