'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';

export default function NewCharacterPage() {
  const { work_id } = useParams() as { work_id: string };
  const router = useRouter();

  const [name, setName] = useState('');
  const [settings, setSettings] = useState('');

  const handleCreate = async () => {
    if (!name.trim()) {
      alert('캐릭터 이름을 입력해주세요.');
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/works/${work_id}/characters`, {
        method: 'POST',
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
        console.error('캐릭터 생성 실패:', errorText);
        alert('캐릭터 생성에 실패했습니다.');
        return;
      }

      const result = await res.json();
      console.log('✅ 캐릭터 생성 완료:', result);
      alert('캐릭터가 생성되었습니다.');

      router.push(`/works/${work_id}/characters`);
    } catch (error) {
      console.error('에러:', error);
      alert('오류로 인해 캐릭터 생성에 실패했습니다.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-bold mb-4">👤 캐릭터 추가</h1>

      <div className="mb-4">
        <label className="block font-medium mb-1">이름</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="캐릭터 이름"
          className="w-full border rounded px-4 py-2"
        />
      </div>

      <div className="mb-6">
        <label className="block font-medium mb-1">설정</label>
        <textarea
          value={settings}
          onChange={(e) => setSettings(e.target.value)}
          placeholder="캐릭터의 배경/성격/능력 등을 입력하세요"
          className="w-full border rounded px-4 py-2 h-32"
        />
      </div>

      <button
        onClick={handleCreate}
        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded"
      >
        캐릭터 생성
      </button>
    </div>
  );
}
