'use client'

import Link from "next/link";
import {useSession, signOut} from 'next-auth/react'

export default function Navbar() {
    const {data:session, status} = useSession();
    if (status ==="loading"){
        return null
    }
    const userId = session?.user?.email;
    return (
        <nav className="w-full px-6 py-4 bg-gray-100 shadow">
            <div className="max-w-5xl mx-auto flex justify-between items-center">
                <Link href="/">Home</Link>
                <Link href="/word">Word</Link>
                <Link href="/works">Works</Link>
                <Link href="/signup">SignUp</Link>
            </div>

            <div className="flex items-center gap-4 whitespace-nowrap">
            {userId ? (
        <>
          <span className="text-sm text-ellipsis overflow-hidden">{userId}</span>
          <button onClick={() => signOut()} className="text-blue-500">Log Out</button>
        </>
      ) : (
        <Link href="/login" className="text-blue-500">Login</Link>
      )}
            </div>
        </nav>
        // 로그인 이랑 페이지 탭 만들기기
        // 데이터 베이스랑 연결
)
}