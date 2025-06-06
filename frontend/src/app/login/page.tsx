"use client"
import { signIn } from "next-auth/react"
import { useSession } from "next-auth/react"
import { redirect } from "next/navigation"

export default function LoginPage() {
  const { data: session } = useSession();
  if (session){
    redirect("/");
  }
  return (
    <div className="flex flex-col items-center p-10">
      <h1 className="text-2xl font-bold mb-4">로그인</h1>
      <button
        onClick={() => signIn("google")}
        className="bg-red-500 text-white px-4 py-2 rounded"
      >
        Google로 로그인
      </button>
    </div>
  )
}
