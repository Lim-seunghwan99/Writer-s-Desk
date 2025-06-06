'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function EditWorldPage() {
  const { work_id, world_id } = useParams() as {
    work_id: string;
    world_id: string;
  };

  const router = useRouter();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchWorldDetail = async () => {
    try {
      const res = await fetch(`http://localhost:8000/works/${work_id}/worlds/${world_id}`);
      if (!res.ok) throw new Error('세계관 정보를 불러올 수 없습니다.');
      const data = await res.json();
      setContent(data.worlds_content);
    } catch (error) {
      console.error('세계관 로딩 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    try {
      const res = await fetch(
        `http://localhost:8000/works/${work_id}/worlds/${world_id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ worlds_content: content }),
        }
      );

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText);
      }

      alert('🌍 세계관이 수정되었습니다!');
      router.push(`/works/${work_id}/worlds`);
    } catch (error) {
      console.error('세계관 수정 실패:', error);
      alert('수정 실패');
    }
  };

  useEffect(() => {
    fetchWorldDetail();
  }, [work_id, world_id]);

  if (loading) return <p className="p-6">로딩 중...</p>;

  return (
    <div className="min-h-screen bg-gray-50 p-6 space-y-4">
      <h1 className="text-xl font-bold mb-4">✏️ 세계관 수정</h1>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        className="w-full h-40 border rounded p-3"
        placeholder="세계관 내용을 입력하세요"
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
