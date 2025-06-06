'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function WorkEditPage() {
  const { work_id } = useParams() as { work_id: string };
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchCurrentTitle = async () => {
    try {
      const res = await fetch(`http://localhost:8000/works/${work_id}/work`);
      if (!res.ok) throw new Error('작품 정보를 불러올 수 없습니다');
      const data = await res.json();
      setTitle(data.works_title);
    } catch (err) {
      console.error(err);
      alert('불러오기 실패');
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
        `http://localhost:8000/works/${work_id}/update_work`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ works_title: title }),
        }
      );

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText);
      }

      alert('✅ 작품 제목이 수정되었습니다!');
      router.push(`/works/${work_id}`);
    } catch (err) {
      console.error('수정 실패:', err);
      alert('제목 수정 실패');
    }
  };

  useEffect(() => {
    fetchCurrentTitle();
  }, [work_id]);

  if (loading) return <div className="p-6">로딩 중...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-xl font-bold mb-4">✏️ 작품 제목 수정</h1>

      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className="w-full border rounded px-4 py-2 mb-4"
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
