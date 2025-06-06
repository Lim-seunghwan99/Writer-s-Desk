'use client';

import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { useState } from 'react';

export default function NewWorkPage() {
  const router = useRouter();
  const { data: session } = useSession();

  const [title, setTitle] = useState('');

  const handleCreate = async () => {
    if (!title.trim()) {
      alert('작품 제목을 입력해주세요.');
      return;
    }

    const userId = session?.user?.email;
    if (!userId) {
      alert('로그인이 필요합니다.');
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/works/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          works_title: title,
          user_id: userId,
        }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        console.error('작품 생성 실패:', errorText);
        alert('작품 생성에 실패했습니다.');
        return;
      }

      const result = await res.json();
      console.log('✅ 작품 생성 완료:', result);

      // 생성된 작품 상세 페이지로 이동
      router.push(`/works/${result.works_id}`);
    } catch (err) {
      console.error('에러 발생:', err);
      alert('서버 오류로 인해 실패했습니다.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-bold mb-4">📚 새 작품 추가</h1>

      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="작품 제목을 입력하세요"
        className="w-full border rounded px-4 py-2 mb-4"
      />

      <button
        onClick={handleCreate}
        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
      >
        생성하기
      </button>
    </div>
  );
}
