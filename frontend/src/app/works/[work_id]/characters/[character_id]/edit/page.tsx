'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function EditCharacterPage() {
  const { work_id, character_id } = useParams() as {
    work_id: string;
    character_id: string;
  };

  const router = useRouter();

  const [name, setName] = useState('');
  const [settings, setSettings] = useState('');
  const [loading, setLoading] = useState(true);

  // 캐릭터 정보 불러오기
  useEffect(() => {
    const fetchCharacter = async () => {
      try {
        const res = await fetch(`http://localhost:8000/works/${work_id}/characters/${character_id}`);
        if (!res.ok) throw new Error('캐릭터 정보를 불러올 수 없습니다.');
        const data = await res.json();
        setName(data.character_name);
        setSettings(data.character_settings);
      } catch (err) {
        console.error(err);
        alert('캐릭터 로딩 실패');
      } finally {
        setLoading(false);
      }
    };

    if (work_id && character_id) fetchCharacter();
  }, [work_id, character_id]);

  // 캐릭터 수정 요청
  const handleUpdate = async () => {
    if (!name.trim()) {
      alert('캐릭터 이름을 입력하세요.');
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/works/${work_id}characters/${character_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          character_name: name,
          character_settings: settings,
        }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText);
      }

      alert('✅ 캐릭터 정보가 수정되었습니다.');
      router.push(`/works/${work_id}/characters`);
    } catch (err) {
      console.error('수정 실패:', err);
      alert('캐릭터 수정 실패');
    }
  };

  if (loading) return <div className="p-6">로딩 중...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6 space-y-4">
      <h1 className="text-xl font-bold">✏️ 캐릭터 수정</h1>

      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="캐릭터 이름"
        className="w-full px-4 py-2 border rounded"
      />

      <textarea
        value={settings}
        onChange={(e) => setSettings(e.target.value)}
        placeholder="캐릭터 설정 내용"
        className="w-full h-40 px-4 py-2 border rounded"
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
