'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {signIn, useSession} from 'next-auth/react'

export default function SignupPage() {
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const router = useRouter();
  const { data:session} = useSession()

  const handleSignup = async () => {
    const res = await fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId, password }),
    });

    const data = await res.json();

    if (!res.ok) {
      setMessage('회원가입 성공! 로그인 페이지로 이동합니다.')
      setTimeout(() => router.push('/login'), 1500);
    }else{
      setMessage(data.error || '오류 발생')
    }
  }

  return (
    <div className = "p-4 space-y-4 min-h-screen flex flex-col justify-center items-center">
      <h2 className = "text-2xl font-bold">회원가입</h2>
      <input className = "border p-2 w-full" placeholder="아이디" value={userId} onChange={(e) => setUserId(e.target.value)} />
      <input className = "border p-2 w-full" placeholder="비밀번호" value={password} onChange={(e) => setPassword(e.target.value)} />

      <button onClick={handleSignup} className="bg-blue-500 text-white px-4 rounded">가입하기</button>

      <hr className="my-4" />

      <button onClick={() => signIn('google')} className="bg-red-500 text-white px-4 py-2 rounded w-full">구글 로그인</button>
      <p>{message}</p>
    </div>
  );
}
