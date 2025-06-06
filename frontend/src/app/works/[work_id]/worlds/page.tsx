'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, useParams } from 'next/navigation';

interface World {
  worlds_id: number;
  worlds_content: string;
  works_id: number;
}

export default function WorldListPage() {
  const { work_id } = useParams();
  const router = useRouter();
  const [worlds, setWorlds] = useState<World[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchWorlds = async () => {
    try {
      const res = await fetch(`http://localhost:8000/works/${work_id}/worlds`);
      if (!res.ok) throw new Error('Failed to fetch worlds');

      const data = await res.json();
      setWorlds(data);
    }catch (error) {
      console.error('세계관 데이터 가져오기 실패:', error);
    }finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    if (work_id){
      fetchWorlds();
    }
  }, [work_id]);

  return (
    <div className="min-h-screen bg-gray-50 p-6 relative">
      <h1 className="text-2xl font-bold mb-6">🌍 세계관 설정</h1>

      <div className="bg-white rounded-2xl shadow-md p-6 space-y-4 max-w-3xl">
        {loading ? (
          <p className="text-gray-500">로딩 중...</p>
        ) : worlds.length === 0 ? (
          <p className="text-gray-500">등록된 세계관이 없습니다.</p>
        ) : (
          worlds.map((world) => (
            <div
              key={world.worlds_id}
              className="flex justify-center items-center bg-black text-white font-semibold rounded px-6 py-3"
            >
            <Link href={`/works/${work_id}/worlds/${world.worlds_id}`}>
              {world.worlds_content}
              </Link>
            </div>
          ))
        )}
      </div>

      <div className="mt-6">
          
      <button onClick={() => router.push(`/works/${work_id}/worlds/new`)} className="px-4 py-2 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition">
          + 세계관 추가
        </button>
      </div>

    </div>
  );
}
