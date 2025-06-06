// components/WordCard.tsx
'use client';

import Link from 'next/link';

interface WordCardProps {
  words_id: number;
  word_name: string;
  word_content: string;
  user_id: string;
}

export default function WordCard({ words_id, word_name, word_content, user_id }: WordCardProps) {
  return (
    <Link href={`/word/${user_id}/${words_id}`}>
      <div className="cursor-pointer bg-white shadow p-4 rounded hover:bg-gray-100">
        <p className="font-bold">{word_name}</p>
        <p className="text-sm text-gray-600">{word_content}</p>
        <p className="text-sm text-gray-600">{user_id}</p>
        <p className="text-sm text-gray-600">{words_id}</p>
      </div>
    </Link>
  );
}
