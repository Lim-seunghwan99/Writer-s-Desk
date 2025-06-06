// app/words/[user_id]/[word_id]/page.tsx

'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import WordExampleItem from '@/components/WordExampleItem';

interface WordDetail {
  word_name: string;
  word_content: string;
  words_id: number;
  user_id: string;
  word_created_time: string;
  word_count: number;
  examples: {
    word_example_content: string;
    example_sequence: number;
  }[];
}

export default function WordDetailPage() {
  const { user_id, word_id } = useParams() as { user_id: string; word_id: string };
  const [word, setWord] = useState<WordDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user_id || !word_id) return;
  
    const fetchWord = async () => {
      try {
        const res = await fetch(`http://localhost:8000/words/${user_id}/id/${word_id}`);
        const data = await res.json();
        console.log("📦 단어 데이터 응답:", data); // ✅ 여기 추가
        setWord(data);
      } catch (error) {
        console.error('단어 불러오기 실패:', error);
      } finally {
        setLoading(false);
      }
    };
  
    fetchWord();
  }, [user_id, word_id]);
  

  const handleDelete = async () => {
    const confirmed = window.confirm("정말 삭제하시겠습니까?");
    if (!confirmed) return;

    try {
      const response = await fetch(`http://localhost:8000/words/${word_id}`, {
        method: "DELETE",
      });
      if (response.ok) {
        alert("삭제되었습니다.");
        window.location.href = `/word`;
      } else {
        alert("삭제에 실패 하였습니다.");
      }
    } catch (error) {
      console.error("삭제 오류:", error);
      alert("삭제 중 오류가 발생했습니다.");
    }
  };

  const updateExampleContent = (sequence: number, newContent: string) => {
    if (!word) return;
    setWord({
      ...word,
      examples: word.examples.map((ex) =>
        ex.example_sequence === sequence
          ? { ...ex, word_example_content: newContent }
          : ex
      ),
    });
  };

  if (loading) return <p>Loading...</p>;
  if (!word) return <p>단어를 찾을 수 없습니다.</p>;

  return (
    <div className="p-6 max-w-3xl space-y-4">
      <h1 className="text-2xl font-bold">{word.word_name}</h1>
      <p className="text-gray-600">{word.word_content}</p>
      <p className="text-sm text-gray-400">작성자: {word.user_id}</p>
      <p className="text-sm text-gray-400">
        작성일: {new Date(word.word_created_time).toLocaleString()}
      </p>

      <div className="mt-4">
        <h2 className="font-semibold">예시 문장</h2>
        <ul className="list-disc pl-5 space-y-1">
          {word.examples?.map((ex) => (
            <li key={ex.example_sequence}>
              <WordExampleItem
                wordId={word.words_id}
                example={ex}
                onUpdate={(newContent) => updateExampleContent(ex.example_sequence, newContent)}
              />
            </li>
          ))}
        </ul>
      </div>

      <button
        onClick={handleDelete}
        className="mt-6 bg-red-500 text-white px-4 py-2 rounded"
      >
        삭제
      </button>
    </div>
  );
}