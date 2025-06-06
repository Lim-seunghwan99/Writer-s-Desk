'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

interface Planning {
  plan_id: number;
  plan_title: string;
  plan_content: string;
  works_id: number;
}

export default function PlanningListPage() {
  const { work_id } = useParams() as { work_id: string };
  const router = useRouter();
  const [plannings, setPlannings] = useState<Planning[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPlannings = async () => {
    try {
      const res = await fetch(`http://localhost:8000/works/${work_id}/plannings`);
      if (!res.ok) throw new Error('기획 목록 불러오기 실패');

      const data = await res.json();
      setPlannings(data);
    } catch (err) {
      console.error('에러:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlannings();
  }, [work_id]);

  return (
    <div className="min-h-screen bg-gray-50 p-6 relative">
      <h1 className="text-2xl font-bold mb-6">📝 기획 목록</h1>

      <div className="bg-white rounded-xl shadow p-6 space-y-4 max-w-3xl">
        {loading ? (
          <p className="text-gray-500">로딩 중...</p>
        ) : plannings.length === 0 ? (
          <p className="text-gray-500">등록된 기획이 없습니다.</p>
        ) : (
          plannings.map((plan) => (
            <div
              key={plan.plan_id}
              className="bg-blue-100 hover:bg-blue-200 cursor-pointer rounded px-4 py-3 font-medium"
              onClick={() =>
                router.push(`/works/${work_id}/plannings/${plan.plan_id}`)
              }
            >
              {plan.plan_title}
            </div>
          ))
        )}
      </div>

      <div className="mt-6">
        <button
          onClick={() => router.push(`/works/${work_id}/plannings/new`)}
          className="px-4 py-2 bg-green-600 text-white rounded-full hover:bg-green-700 shadow"
        >
          + 기획 추가
        </button>
      </div>
      
    </div>
  );
}
