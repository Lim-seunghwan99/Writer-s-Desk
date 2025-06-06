'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function EditEpisodePage() {
  const { work_id, episode_id } = useParams() as {
    work_id: string;
    episode_id: string;
  };

  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const fetchEpisode = async () => {
    try {
      const res = await fetch(`http://localhost:8000/episodes/${work_id}/${episode_id}`);
      if (!res.ok) throw new Error('에피소드를 불러오지 못했습니다');
      const data = await res.json();
      setContent(data.episode_content);
    } catch (err) {
      console.error(err);
      alert('에피소드 불러오기 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    if (!content.trim()) {
      alert('내용을 입력해주세요.');
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/episodes/${work_id}/${episode_id}/episode_content`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          episode_content: content,
        }),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText);
      }

      alert('✅ 에피소드가 수정되었습니다!');
      router.push(`/works/${work_id}/episodes/${episode_id}`);
    } catch (err) {
      console.error('수정 실패:', err);
      alert('수정 중 오류 발생');
    }
  };

  useEffect(() => {
    fetchEpisode();
  }, [work_id, episode_id]);

  if (loading) return <div className="p-6">로딩 중...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6 space-y-4">
      <h1 className="text-xl font-bold">✍️ 에피소드 내용 수정</h1>

      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        className="w-full h-48 border rounded p-4"
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
