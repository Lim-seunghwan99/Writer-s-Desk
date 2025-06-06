'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

interface Planning {
  plan_id: number;
  plan_title: string;
  plan_content: string;
  works_id: number;
}

export default function PlanningDetailPage() {
  const { work_id, plan_id } = useParams() as {
    work_id: string;
    plan_id: string;
  };

  const router = useRouter();
  const [plan, setPlan] = useState<Planning | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchPlan = async () => {
    try {
      const res = await fetch(
        `http://localhost:8000/works/${work_id}/plannings/${plan_id}`
      );
      if (!res.ok) throw new Error('기획 정보를 찾을 수 없습니다.');
      const data = await res.json();
      setPlan(data);
    } catch (error) {
      console.error('에러:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    const confirmDelete = confirm('정말로 이 기획을 삭제하시겠습니까?');
    if (!confirmDelete) return;

    try {
      const res = await fetch(
        `http://localhost:8000/works/${work_id}/plannings/${plan_id}`,
        {
          method: 'DELETE',
        }
      );

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`삭제 실패: ${errText}`);
      }

      alert('삭제되었습니다.');
      router.push(`/works/${work_id}`);
    } catch (err) {
      console.error('삭제 에러:', err);
      alert('삭제에 실패했습니다.');
    }
  };

  useEffect(() => {
    fetchPlan();
  }, [work_id, plan_id]);

  if (loading) return <div className="p-6">로딩 중...</div>;
  if (!plan) return <div className="p-6 text-red-500">기획을 찾을 수 없습니다.</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-6 space-y-6">
      <h1 className="text-2xl font-bold">📝 {plan.plan_title}</h1>

      <div className="bg-white rounded p-4 shadow whitespace-pre-wrap text-gray-800">
        {plan.plan_content}
      </div>

      <button
          className="px-4 py-2 bg-green-600 text-white rounded-full shadow-lg hover:bg-green-700 transition"
          onClick={() => router.push(`/works/${work_id}/plannings/${plan_id}/edit`)}
        >
          ✏️ 기획 수정
        </button>

        <button
          className="px-4 py-2 bg-red-600 text-white rounded-full shadow-lg hover:bg-red-700 transition"
          onClick={handleDelete}
        >
          ❌ 기획 삭제
        </button>
    </div>
  );
}
