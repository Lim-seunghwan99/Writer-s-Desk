'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

interface World {
  worlds_id: number;
  worlds_content: string;
  works_id: number;
}

export default function WorldDetailPage() {
  const { work_id, world_id } = useParams() as {
    work_id: string;
    world_id: string;
  };

  const [world, setWorld] = useState<World | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchWorld = async () => {
    try {
      const res = await fetch(
        `http://localhost:8000/works/${work_id}/worlds/${world_id}`
      );
      if (!res.ok) throw new Error('세계관 정보를 불러올 수 없습니다.');
      const data = await res.json();
      setWorld(data);
    } catch (error) {
      console.error('에러:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorld();
  }, [work_id, world_id]);

  const handleDelete = async () => {
    const confirmed = confirm('정말 삭제하시겠습니까?');
    if(!confirmed) return;

    try {
      const res = await fetch(
        `http://localhost:8000/works/${work_id}/worlds/${world_id}`,
        {
          method: 'DELETE',
        }
      );
      if (!res.ok) {
        const errorText = await res.text();
        console.error('세계관 삭제 실패:', errorText);
        alert('세계관 삭제 실패');
        return;
    }

    const result = await res.json();
    console.log('세계관 삭제 성공:', result);
    alert('세계관 삭제 성공');
    router.push(`/works/${work_id}/worlds`);
  } catch (error) {
    console.error('세계관 삭제 중 오류 발생:', error);
    alert('세계관 삭제 중 오류가 발생했습니다. 다시 시도해주세요.');
  }
};

if (loading) return <div className="p-6">로딩 중...</div>;
if (!world) return <div className="p-6 text-red-500">세계관을 찾을 수 없습니다.</div>;


  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-bold mb-6">🌍 세계관 상세</h1>
      <div className="bg-white rounded-lg p-6 shadow">
        <p className="whitespace-pre-wrap text-gray-800">{world.worlds_content}</p>
      </div>
      <button
          className="px-4 py-2 bg-green-600 text-white rounded-full shadow-lg hover:bg-green-700 transition"
          onClick={() => router.push(`/works/${work_id}/worlds/${world_id}/edit`)}
        >
          ✏️ 세계관 수정
        </button>

        <button
          className="px-4 py-2 bg-red-600 text-white rounded-full shadow-lg hover:bg-red-700 transition"
          onClick={handleDelete}
        >
          ❌ 세계관 삭제
        </button>
    </div>
  );
}
