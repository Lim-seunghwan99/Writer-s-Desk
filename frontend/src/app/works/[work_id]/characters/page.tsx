'use client';

import React, {useState, useEffect} from 'react';
import { useParams, useRouter } from 'next/navigation';

interface Character {
  character_id: number;
  character_name: string;
  character_settings: string;
  works_id: number;
}

export default function CharacterListPage() {
  const { work_id } = useParams() as { work_id: string };
  const router = useRouter();

  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchCharacters = async () => {
    try{
      const res = await fetch(`http://localhost:8000/works/${work_id}/characters`);
      if (!res.ok) throw new Error('캐릭터 데이터를 불러올 수 없습니다.');

      const data = await res.json();
      setCharacters(data);
    } catch (error) {
      console.error('캐릭터 데이터 가져오기 실패:', error);
    }finally {
      setLoading(false);
    }
    };

  useEffect(() => {
    if (work_id) {
      fetchCharacters();
    }
  }, [work_id]);

  return (
    <div className="min-h-screen bg-gray-50 p-6 relative">

      {/* 제목 */}
      <h1 className="text-2xl font-bold mb-6">캐릭터 설정</h1>

      {/* 캐릭터 리스트 */}
      <div className="bg-white rounded-2xl shadow-md p-6 space-y-4 max-w-3xl">
        {loading ? (
          <p className="text-gray-500">로딩중...</p>
        ) : characters.length ===0 ? (
          <p className="text-gray-500">등록된 캐릭터가 없습니다.</p>
        ) : (
          characters.map((char) => (
            <div
            onClick={() => router.push(`/works/${work_id}/characters/${char.character_id}`)}
            key={char.character_id}
            className="flex justify-between items-center bg-gray-100 rounded-lg p-4"
            >
              {char.character_name}
              </div>
              ))
        )}
      </div>
      {/* 하단 우측 버튼 */}
      <div className="mt-6">
      <button onClick={() => router.push(`/works/${work_id}/characters/new`)} className="px-4 py-2 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition">
          + 캐릭터 추가
        </button>
      </div>
    </div>
  );
}
