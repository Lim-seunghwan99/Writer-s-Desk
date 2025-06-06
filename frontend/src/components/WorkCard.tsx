'use client';

import Link from 'next/link';

interface WorkCardProps {
    id: number;
    title: string;
    tag?: string;
  }

export default function WorkCard({id, title, tag}: WorkCardProps) {
    return (
      <Link href={`/works/${id}`}>
          <div className="cursor-pointer bg-white p-4 rounded-lg shadow-sm hover:bg-gray-100 flex items-center justify-between">
            <span className="text-lg font-medium">{title}</span>
            {tag && (
              <span className="ml-4 bg-purple-200 text-purple-800 text-xs font-semibold px-3 py-1 rounded-full">
                {tag}
              </span>
            )}
          </div>
        </Link>
      );
    };