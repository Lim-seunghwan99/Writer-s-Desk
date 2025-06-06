'use client'

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

export default function NewWorldPage() {
    const { work_id } = useParams() as {work_id: string};
    const router = useRouter();
    const [content, setContent] = useState('');

    const handleCreate = async ()=>{
        if (!content.trim()){
            alert('내용을 입력해주세요');
            return;
        }
        try {
            const res = await fetch(`http://localhost:8000/works/${work_id}/worlds`,{
                method: 'POST',
                headers:{ 'Content-Type': 'application/json'},
                body: JSON.stringify({worlds_content: content}),
        }); 
        if (!res.ok){
            const errorText = await res.text();
            console.error('세계관 추가 실패:', errorText);
            alert('세계관 추가 실패');
            return;
        }
        const data = await res.json();
        console.log('세계관 추가 성공:', data);

        router.push(`/works/${work_id}/worlds`);
    } catch (error) {
        console.error('세계관 추가 중 오류 발생:', error);
        alert('세계관 추가 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
};
    return (
        <div className="p-6 bg-gray-50 min-h-screen">
        <h1 className="text-2xl font-bold mb-4">🌍 세계관 추가</h1>
  
        <textarea
          placeholder="세계관 내용을 입력하세요"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full h-40 p-4 border rounded mb-4"
        />
  
        <button
          onClick={handleCreate}
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
        >
          생성하기
        </button>
      </div>
    );
  }