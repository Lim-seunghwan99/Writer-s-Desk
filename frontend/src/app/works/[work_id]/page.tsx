'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
interface Episode {
  episode_id: number;
  episode_content: string;
  works_id: number;
}

interface WorkDetail {
  works_id: number;
  works_title: string;
  user_id: string;
  worlds: any[];
  characters: any[];
  plannings: any[];
  episodes: Episode[];
}

export default function WorkDetailPage() {
  const { work_id } = useParams() as { work_id: string };
  const [work, setWork] = useState<WorkDetail | null>(null);
  const [loading, setLoading] = useState(true);

  const router = useRouter();

  const fetchWorkDetail = async () => {
    try {
      const res = await fetch(`http://localhost:8000/works/${work_id}/work`);
      if (!res.ok) throw new Error('API 요청 실패');
      const data = await res.json();
      setWork(data);
    } catch (error) {
      console.error('작품 정보 불러오기 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (work_id) {
      fetchWorkDetail();
    }
  }, [work_id]);

  if (loading) return <p className="text-center text-gray-500">로딩 중...</p>;
  if (!work) return <p className="text-center text-red-500">작품을 불러오지 못했습니다.</p>;

  const handleDelete = async () => {
    const confirmDelete = confirm("정말로 이 작품을 삭제 하시겠습니까?")
    if (!confirmDelete) return;

    try{
      const res = await fetch(`http://localhost:8000/works/${work_id}`, {
        method:"DELETE",
      });
      
      if (!res.ok){
        const errorText = await res.text();
        console.error("삭제 실패:", errorText);
        alert("자가품 삭제에 실패 했습니다.");
        return;
      }

      const deleted = await res.json();
      console.log('삭제 완료:', deleted);

      alert("작품이 삭제 되었습니다.");
      router.push("/works");
    } catch (error) {
      console.error("삭제 중 오류 발생:",error);
      alert("오류로 인해 삭제에 실패 했습니다.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-2xl font-bold mb-6">🎬 {work.works_title}</h1>

      <div className="grid grid-cols-3 gap-4 mb-8">

        <button onClick={() => router.push(`/works/${work_id}/plannings`)} className="py-3 bg-white border rounded hover:bg-gray-100 font-semibold">
          기획 설정
        </button>
        <button onClick={() => router.push(`/works/${work_id}/worlds`)} className="py-3 bg-white border rounded hover:bg-gray-100 font-semibold">
          세계관 설정
        </button>
        <button onClick={() => router.push(`/works/${work_id}/characters`)} className="py-3 bg-white border rounded hover:bg-gray-100 font-semibold">
          캐릭터 설정
        </button>
      </div>

      <hr className="mb-6" />

      <h2 className="text-lg font-semibold mb-4">📘 에피소드 목록</h2>
      <div className="grid grid-cols-4 gap-4">
        {work.episodes.map((ep,index) => (
          <Link
            key={ep.episode_id}
            href={`/works/${work_id}/episodes/${ep.episode_id}`}
            className="bg-white p-3 rounded shadow-sm hover:bg-gray-100 block text-center"
          >
            EP. {index + 1}
          </Link>
        ))}
      </div>

      <div className="mt-10 text-center">
        <Link href={`/works/${work_id}/episodes/new`}>
          <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
            ➕ 에피소드 추가
          </button>
        </Link>
      </div>
      <div className="mt-10 text-center">
      <button
    onClick={() => router.push(`/works/${work_id}/edit`)}
    className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
  >
    🗑 작품 수정
  </button>
  <button
    onClick={handleDelete}
    className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
  >
    🗑 작품 삭제
  </button>
</div>


    </div>
  );
}
