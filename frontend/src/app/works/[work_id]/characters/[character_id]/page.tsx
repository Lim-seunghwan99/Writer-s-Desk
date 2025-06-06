'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

interface Character {
  character_id: number;
  character_name: string;
  character_settings: string;
  works_id: number;
}

export default function CharacterDetailPage() {
  const { work_id, character_id } = useParams() as {
    work_id: string;
    character_id: string;
  };

  const router = useRouter();
  const [character, setCharacter] = useState<Character | null>(null);
  const [loading, setLoading] = useState(true);
  const [imageUrl, setImageUrl] = useState('');
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    if (!work_id || !character_id) return;

    const fetchCharacter = async () => {
      try {
        const res = await fetch(`http://localhost:8000/works/${work_id}/characters/${character_id}`);
        if (!res.ok) throw new Error('캐릭터 정보를 찾을 수 없습니다.');
        const data = await res.json();
        setCharacter(data);
      } catch (err) {
        console.error('에러:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCharacter();
  }, [work_id, character_id]);

  const handleDeleteCharacter = async () => {
    if (!work_id || !character_id) return;
    const confirmDelete = confirm('정말로 이 캐릭터를 삭제하시겠습니까?');
    if (!confirmDelete) return;

    try {
      const res = await fetch(`http://localhost:8000/works/${work_id}characters/${character_id}`, {
        method: 'DELETE',
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText);
      }

      alert('✅ 캐릭터가 삭제되었습니다.');
      router.push(`/works/${work_id}/characters`);
    } catch (err) {
      console.error('삭제 실패:', err);
      alert('삭제 중 오류 발생');
    }
  };

  const handleGenerateImage = async () => {
    if (!character?.character_settings) {
      alert('캐릭터 설정이 비어 있습니다.');
      return;
    }

    setGenerating(true);
    try {
      const res = await fetch('http://192.168.1.10:8100/generate-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: character.character_settings }),
      });

      if (!res.ok) throw new Error('이미지 생성 실패');

      const data = await res.json();

      if (data.image_urls?.length > 0) {
        const relativeUrl = data.image_urls[0];
        const fullUrl = `http://192.168.1.10:8100${relativeUrl}`;
        setImageUrl(fullUrl);
      } else {
        throw new Error('이미지 URL이 비어 있습니다.');
      }
    } catch (err) {
      console.error('이미지 생성 오류:', err);
      alert('이미지 생성 실패');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <div className="p-6">로딩 중...</div>;
  if (!character) return <div className="p-6 text-red-500">캐릭터를 찾을 수 없습니다.</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-bold mb-4">👤 캐릭터 상세</h1>

      <div className="bg-white rounded-lg p-6 shadow space-y-4">
        <p><strong>이름:</strong> {character.character_name}</p>
        <p><strong>설정:</strong></p>
        <p className="whitespace-pre-wrap">{character.character_settings}</p>
      </div>

      <div className="flex flex-wrap gap-4 mt-6">
        <button
          className="px-4 py-2 bg-green-600 text-white rounded-full shadow-lg hover:bg-green-700 transition"
          onClick={() => router.push(`/works/${work_id}/characters/${character_id}/edit`)}
        >
          ✏️ 캐릭터 수정
        </button>

        <button
          className="px-4 py-2 bg-red-600 text-white rounded-full shadow-lg hover:bg-red-700 transition"
          onClick={handleDeleteCharacter}
        >
          ❌ 캐릭터 삭제
        </button>

        <button
          className="px-4 py-2 bg-purple-600 text-white rounded-full shadow-lg hover:bg-purple-700 transition"
          onClick={handleGenerateImage}
          disabled={generating}
        >
          {generating ? '이미지 생성 중...' : '🎨 이미지 생성'}
        </button>
      </div>

      {imageUrl && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-2">🖼️ 생성된 이미지</h2>
          <img src={imageUrl} alt="생성된 캐릭터 이미지" className="w-full max-w-md rounded shadow" />
        </div>
      )}
    </div>
  );
}
